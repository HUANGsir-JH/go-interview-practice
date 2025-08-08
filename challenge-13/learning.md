# Go 中 SQL 数据库操作学习资料

## Go 中的 SQL 数据库

Go 通过标准 `database/sql` 包提供了对 SQL 数据库的优秀支持。本挑战聚焦于使用 SQLite 实现 CRUD 操作，但这些概念同样适用于 MySQL、PostgreSQL 等其他 SQL 数据库。

### database/sql 包

`database/sql` 包为 SQL（或类似 SQL）数据库提供了一个通用接口。它具备以下功能：

- 管理连接池  
- 处理事务
- 提供预处理语句
- 支持多种数据库的驱动

```go
import (
    "database/sql"
    _ "github.com/mattn/go-sqlite3" // 注意下划线导入
)
```

下划线导入（`_`）用于仅导入包的副作用（此处是注册数据库驱动）。

### 打开数据库连接

```go
db, err := sql.Open("sqlite3", "path/to/database.db")
if err != nil {
    return nil, err
}

// 测试连接
if err = db.Ping(); err != nil {
    return nil, err
}

return db, nil
```

`sql.Open()` 函数最初并不会实际建立数据库连接。只有在调用 `Ping()` 或执行查询时才会建立连接。

### 执行简单查询

可以使用 `db.Exec()` 执行不返回行的简单 SQL 语句：

```go
result, err := db.Exec(
    "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, quantity INTEGER, category TEXT)"
)
if err != nil {
    return err
}
```

对于 `INSERT` 操作，可以获取最后插入的 ID：

```go
result, err := db.Exec(
    "INSERT INTO products (name, price, quantity, category) VALUES (?, ?, ?, ?)",
    product.Name, product.Price, product.Quantity, product.Category
)
if err != nil {
    return err
}

// 获取插入行的 ID
id, err := result.LastInsertId()
if err != nil {
    return err
}
product.ID = id
```

### 查询数据

要查询并检索数据，请使用 `db.Query()` 或 `db.QueryRow()`：

```go
// 获取多行数据
rows, err := db.Query("SELECT id, name, price, quantity, category FROM products WHERE category = ?", category)
if err != nil {
    return nil, err
}
defer rows.Close() // 使用完毕后始终关闭 rows

var products []*Product
for rows.Next() {
    p := &Product{}
    err := rows.Scan(&p.ID, &p.Name, &p.Price, &p.Quantity, &p.Category)
    if err != nil {
        return nil, err
    }
    products = append(products, p)
}

// 检查遍历 rows 时的错误
if err = rows.Err(); err != nil {
    return nil, err
}

return products, nil
```

对于单行数据，使用 `QueryRow()`：

```go
row := db.QueryRow("SELECT id, name, price, quantity, category FROM products WHERE id = ?", id)

p := &Product{}
err := row.Scan(&p.ID, &p.Name, &p.Price, &p.Quantity, &p.Category)
if err != nil {
    if err == sql.ErrNoRows {
        return nil, fmt.Errorf("ID 为 %d 的产品未找到", id)
    }
    return nil, err
}

return p, nil
```

### 预处理语句

对于需要多次执行的查询，可以使用预处理语句以提高性能：

```go
stmt, err := db.Prepare("UPDATE products SET quantity = ? WHERE id = ?")
if err != nil {
    return err
}
defer stmt.Close()

for id, quantity := range updates {
    _, err := stmt.Exec(quantity, id)
    if err != nil {
        return err
    }
}
```

### 事务

事务确保一组操作要么全部成功，要么全部失败：

```go
// 开始事务
tx, err := db.Begin()
if err != nil {
    return err
}
defer func() {
    if err != nil {
        tx.Rollback() // 出错时回滚
    }
}()

stmt, err := tx.Prepare("UPDATE products SET quantity = ? WHERE id = ?")
if err != nil {
    return err
}
defer stmt.Close()

for id, quantity := range updates {
    result, err := stmt.Exec(quantity, id)
    if err != nil {
        return err
    }
    
    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return err
    }
    
    if rowsAffected == 0 {
        return fmt.Errorf("ID 为 %d 的产品未找到", id)
    }
}

// 提交事务
return tx.Commit()
```

### 参数绑定与防止 SQL 注入

始终使用参数绑定而非字符串拼接来防止 SQL 注入：

```go
// 不要这样做 - 易受 SQL 注入攻击
query := fmt.Sprintf("SELECT * FROM products WHERE category = '%s'", category)

// 要这样做 - 使用参数绑定
rows, err := db.Query("SELECT * FROM products WHERE category = ?", category)
```

不同数据库驱动使用不同的占位符风格：

- SQLite、MySQL：`?`
- PostgreSQL：`$1`, `$2` 等
- Oracle：`:name`

### 处理 NULL 值

SQL 数据库可能包含 NULL 值。Go 在 `database/sql` 包中提供了特殊类型来处理这些情况：

```go
import (
    "database/sql"
)

type Product struct {
    ID       int64
    Name     string
    Price    float64
    Quantity int
    Category sql.NullString // 可以为 NULL
}

// 扫描时
var category sql.NullString
err := row.Scan(&id, &name, &price, &quantity, &category)

// 使用时
if category.Valid {
    fmt.Println(category.String)
} else {
    fmt.Println("Category 为 NULL")
}
```

### 错误处理

需要检查多种错误类型：

```go
if err == sql.ErrNoRows {
    // 未返回任何行（不一定是错误）
    return nil, fmt.Errorf("产品未找到")
}

// 检查唯一约束冲突
if strings.Contains(err.Error(), "UNIQUE constraint failed") {
    return nil, fmt.Errorf("名称为该的产品已存在")
}
```

### 连接池

`database/sql` 包自动处理连接池。你可以控制池的行为：

```go
db.SetMaxOpenConns(25)  // 最大打开连接数
db.SetMaxIdleConns(25)  // 最大空闲连接数
db.SetConnMaxLifetime(5 * time.Minute) // 连接可复用的最大时间
```

### 最佳实践

1. 始终关闭如 rows 和 statements 等资源  
2. 对必须作为一个整体成功的操作使用事务  
3. 永远不要通过字符串拼接构建 SQL 查询  
4. 检查特定错误，如 `sql.ErrNoRows`  
5. 保持数据库连接在整个应用程序生命周期内打开  
6. 对复杂应用考虑使用 ORM 或查询生成器