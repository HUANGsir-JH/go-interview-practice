# 挑战13提示：使用Go进行SQL数据库操作

## 提示1：数据库设置与连接
首先设置SQLite数据库并创建products表：
```go
import (
    "database/sql"
    _ "github.com/mattn/go-sqlite3"
)

func InitDB(dbPath string) (*sql.DB, error) {
    db, err := sql.Open("sqlite3", dbPath)
    if err != nil {
        return nil, err
    }
    
    // 创建products表
    createTableSQL := `
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );`
    
    _, err = db.Exec(createTableSQL)
    if err != nil {
        return nil, err
    }
    
    return db, nil
}
```

## 提示2：产品结构体与模型
定义与数据库模式匹配的Product结构体：
```go
type Product struct {
    ID          int     `json:"id"`
    Name        string  `json:"name"`
    Description string  `json:"description"`
    Price       float64 `json:"price"`
    Stock       int     `json:"stock"`
    CreatedAt   string  `json:"created_at"`
}
```

## 提示3：使用参数绑定创建产品
使用参数绑定来防止SQL注入：
```go
func CreateProduct(db *sql.DB, product Product) (int, error) {
    query := `
    INSERT INTO products (name, description, price, stock) 
    VALUES (?, ?, ?, ?)`
    
    result, err := db.Exec(query, product.Name, product.Description, product.Price, product.Stock)
    if err != nil {
        return 0, fmt.Errorf("创建产品失败: %w", err)
    }
    
    id, err := result.LastInsertId()
    if err != nil {
        return 0, fmt.Errorf("获取最后插入ID失败: %w", err)
    }
    
    return int(id), nil
}
```

## 提示4：根据ID获取产品
使用QueryRow获取单条记录：
```go
func GetProduct(db *sql.DB, id int) (*Product, error) {
    query := `
    SELECT id, name, description, price, stock, created_at 
    FROM products 
    WHERE id = ?`
    
    var product Product
    err := db.QueryRow(query, id).Scan(
        &product.ID,
        &product.Name,
        &product.Description,
        &product.Price,
        &product.Stock,
        &product.CreatedAt,
    )
    
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("未找到ID为%d的产品", id)
        }
        return nil, fmt.Errorf("获取产品失败: %w", err)
    }
    
    return &product, nil
}
```

## 提示5：更新产品并进行验证
在更新前检查产品是否存在：
```go
func UpdateProduct(db *sql.DB, id int, product Product) error {
    // 首先检查产品是否存在
    _, err := GetProduct(db, id)
    if err != nil {
        return err
    }
    
    query := `
    UPDATE products 
    SET name = ?, description = ?, price = ?, stock = ? 
    WHERE id = ?`
    
    result, err := db.Exec(query, product.Name, product.Description, product.Price, product.Stock, id)
    if err != nil {
        return fmt.Errorf("更新产品失败: %w", err)
    }
    
    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }
    
    if rowsAffected == 0 {
        return fmt.Errorf("没有行被更新")
    }
    
    return nil
}
```

## 提示6：删除产品
实现删除操作并检查存在性：
```go
func DeleteProduct(db *sql.DB, id int) error {
    query := `DELETE FROM products WHERE id = ?`
    
    result, err := db.Exec(query, id)
    if err != nil {
        return fmt.Errorf("删除产品失败: %w", err)
    }
    
    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }
    
    if rowsAffected == 0 {
        return fmt.Errorf("未找到ID为%d的产品", id)
    }
    
    return nil
}
```

## 提示7：带过滤条件列出产品
使用Query获取多条记录，并实现可选过滤功能：
```go
func ListProducts(db *sql.DB, filters map[string]interface{}) ([]Product, error) {
    query := "SELECT id, name, description, price, stock, created_at FROM products"
    args := []interface{}{}
    conditions := []string{}
    
    // 动态添加过滤条件
    if name, ok := filters["name"]; ok {
        conditions = append(conditions, "name LIKE ?")
        args = append(args, "%"+name.(string)+"%")
    }
    
    if minPrice, ok := filters["min_price"]; ok {
        conditions = append(conditions, "price >= ?")
        args = append(args, minPrice)
    }
    
    if len(conditions) > 0 {
        query += " WHERE " + strings.Join(conditions, " AND ")
    }
    
    query += " ORDER BY created_at DESC"
    
    rows, err := db.Query(query, args...)
    if err != nil {
        return nil, fmt.Errorf("列出产品失败: %w", err)
    }
    defer rows.Close()
    
    var products []Product
    for rows.Next() {
        var product Product
        err := rows.Scan(&product.ID, &product.Name, &product.Description, 
                        &product.Price, &product.Stock, &product.CreatedAt)
        if err != nil {
            return nil, fmt.Errorf("扫描产品失败: %w", err)
        }
        products = append(products, product)
    }
    
    return products, nil
}
```

## 提示8：事务支持
为修改多条记录的操作实现事务：
```go
func BulkUpdatePrices(db *sql.DB, updates map[int]float64) error {
    tx, err := db.Begin()
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }
    
    // 使用defer处理panic或错误时的回滚
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
            panic(r)
        }
    }()
    
    query := "UPDATE products SET price = ? WHERE id = ?"
    stmt, err := tx.Prepare(query)
    if err != nil {
        tx.Rollback()
        return fmt.Errorf("准备语句失败: %w", err)
    }
    defer stmt.Close()
    
    for id, price := range updates {
        _, err := stmt.Exec(price, id)
        if err != nil {
            tx.Rollback()
            return fmt.Errorf("更新产品%d的价格失败: %w", id, err)
        }
    }
    
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }
    
    return nil
}
```

## 关键数据库概念：
- **参数绑定**：始终使用?占位符以防止SQL注入
- **错误处理**：检查sql.ErrNoRows以处理未找到的情况
- **资源清理**：始终对rows和statements使用defer Close()
- **事务**：使用Begin/Commit/Rollback确保多操作的一致性
- **预处理语句**：对重复查询且参数不同的情况使用Prepare()
- **上下文**：使用带有context的方法（QueryContext, ExecContext）以支持取消操作