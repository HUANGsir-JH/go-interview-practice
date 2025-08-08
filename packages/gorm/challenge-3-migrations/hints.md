# GORM 迁移挑战提示

## 提示 1：理解迁移版本

每个迁移都应具有唯一的版本号，以表示应用顺序。使用 `MigrationVersion` 表来跟踪已应用的迁移。

## 提示 2：数据库连接设置

使用 `gorm.Open()` 配合 SQLite 驱动程序。此处不要自动迁移所有模型——让迁移处理模式变更：

```go
func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    // 创建迁移追踪表
    db.AutoMigrate(&MigrationVersion{})
    return db, nil
}
```

## 提示 3：安全地运行迁移

检查迁移是否已存在，使用事务，并在成功应用后记录迁移版本：

```go
func RunMigration(db *gorm.DB, version int) error {
    // 检查是否已应用
    var existing MigrationVersion
    if err := db.Where("version = ?", version).First(&existing).Error; err == nil {
        return nil // 已经应用过
    }
    
    tx := db.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()
    
    // 根据版本号应用迁移
    switch version {
    case 1:
        if err := tx.AutoMigrate(&Product{}).Error; err != nil {
            tx.Rollback()
            return err
        }
    case 2:
        if err := tx.AutoMigrate(&Category{}).Error; err != nil {
            tx.Rollback()
            return err
        }
    case 3:
        if err := tx.Exec("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0").Error; err != nil {
            tx.Rollback()
            return err
        }
    }
    
    // 记录迁移
    migration := MigrationVersion{Version: version, AppliedAt: time.Now()}
    if err := tx.Create(&migration).Error; err != nil {
        tx.Rollback()
        return err
    }
    
    return tx.Commit().Error
}
```

## 提示 4：迁移回滚

按相反顺序应用回滚操作并删除迁移记录：

```go
func RollbackMigration(db *gorm.DB, targetVersion int) error {
    current, err := GetMigrationVersion(db)
    if err != nil {
        return err
    }
    
    for version := current; version > targetVersion; version-- {
        tx := db.Begin()
        
        switch version {
        case 3:
            tx.Exec("ALTER TABLE products DROP COLUMN stock")
        case 2:
            tx.Migrator().DropTable(&Category{})
        case 1:
            tx.Migrator().DropTable(&Product{})
        }
        
        tx.Where("version = ?", version).Delete(&MigrationVersion{})
        tx.Commit()
    }
    return nil
}
```

## 提示 5：追踪迁移版本

查询 `MigrationVersion` 表以获取最高版本号：

```go
func GetMigrationVersion(db *gorm.DB) (int, error) {
    var migration MigrationVersion
    err := db.Order("version DESC").First(&migration).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return 0, nil
        }
        return 0, err
    }
    return migration.Version, nil
}
```

## 提示 6：数据填充

创建带有正确关系的示例数据，并使用事务确保一致性：

```go
func SeedData(db *gorm.DB) error {
    categories := []Category{
        {Name: "科技", Description: "科技产品"},
        {Name: "体育", Description: "体育用品"},
    }
    
    for _, cat := range categories {
        db.Create(&cat)
    }
    
    products := []Product{
        {Name: "笔记本电脑", Price: 999.99, CategoryID: 1, Stock: 10, SKU: "LAP-001"},
        {Name: "足球", Price: 29.99, CategoryID: 2, Stock: 50, SKU: "SPT-001"},
    }
    
    for _, prod := range products {
        db.Create(&prod)
    }
    
    return nil
}
```

## 提示 7：创建产品

验证必填字段并检查类别是否存在：

```go
func CreateProduct(db *gorm.DB, product *Product) error {
    // 验证必填字段
    if product.Name == "" || product.Price <= 0 || product.SKU == "" {
        return errors.New("缺少必填字段")
    }
    
    // 检查类别是否存在
    var category Category
    if err := db.First(&category, product.CategoryID).Error; err != nil {
        return errors.New("类别未找到")
    }
    
    return db.Create(product).Error
}
```

## 提示 8：按类别查询产品

使用 `Where()` 进行过滤并实现分页：

```go
func GetProductsByCategory(db *gorm.DB, categoryID uint, page, pageSize int) ([]Product, int64, error) {
    var products []Product
    var total int64
    
    query := db.Where("category_id = ?", categoryID)
    query.Model(&Product{}).Count(&total)
    
    offset := (page - 1) * pageSize
    err := query.Offset(offset).Limit(pageSize).Find(&products).Error
    
    return products, total, err
}
```

## 迁移实现模式

### 版本 1：基础产品表
```go
func CreateProductsTable(db *gorm.DB) error {
    return db.AutoMigrate(&Product{})
}
```

### 版本 2：添加类别表
```go
func AddCategoriesTable(db *gorm.DB) error {
    // 创建类别表
    if err := db.AutoMigrate(&Category{}); err != nil {
        return err
    }
    
    // 向产品表添加 category_id 字段
    return db.Exec("ALTER TABLE products ADD COLUMN category_id INTEGER").Error
}
```

### 版本 3：添加库存字段
```go
func AddInventoryFields(db *gorm.DB) error {
    // 向产品表添加新列
    return db.Exec(`
        ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0;
        ALTER TABLE products ADD COLUMN sku VARCHAR(255) UNIQUE;
        ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1;
    `).Error
}
```

## 事务模式

### 安全的迁移执行
```go
func RunMigration(db *gorm.DB, version int) error {
    tx := db.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()
    
    // 检查是否已应用
    var existing MigrationVersion
    if err := tx.Where("version = ?", version).First(&existing).Error; err == nil {
        return nil // 已经应用过
    }
    
    // 应用迁移
    if err := applyMigration(tx, version); err != nil {
        tx.Rollback()
        return err
    }
    
    // 记录迁移
    migration := MigrationVersion{Version: version, AppliedAt: time.Now()}
    if err := tx.Create(&migration).Error; err != nil {
        tx.Rollback()
        return err
    }
    
    return tx.Commit().Error
}
```

## 错误处理

1. **迁移已应用** - 应用前先检查
2. **无效的迁移版本** - 对未知版本返回错误
3. **数据库错误** - 妥善处理 SQL 错误
4. **回滚错误** - 确保回滚操作是安全的

## 测试策略

### 测试迁移序列
```go
// 测试按顺序运行迁移
err := RunMigration(db, 1)
assert.NoError(t, err)

err = RunMigration(db, 2)
assert.NoError(t, err)

err = RunMigration(db, 3)
assert.NoError(t, err)

// 验证最终状态
assert.True(t, db.Migrator().HasTable(&Product{}))
assert.True(t, db.Migrator().HasTable(&Category{}))
```

### 测试回滚
```go
// 运行迁移
RunMigration(db, 1)
RunMigration(db, 2)
RunMigration(db, 3)

// 回滚到版本 2
err := RollbackMigration(db, 2)
assert.NoError(t, err)

// 验证状态
version, _ := GetMigrationVersion(db)
assert.Equal(t, 2, version)
```

## 数据填充模式

### 创建示例数据
```go
func SeedData(db *gorm.DB) error {
    // 创建类别
    categories := []Category{
        {Name: "科技", Description: "科技产品"},
        {Name: "体育", Description: "体育用品"},
        {Name: "食品", Description: "食品类商品"},
    }
    
    for _, cat := range categories {
        if err := db.Create(&cat).Error; err != nil {
            return err
        }
    }
    
    // 创建产品
    products := []Product{
        {Name: "笔记本电脑", Price: 999.99, CategoryID: 1, Stock: 10, SKU: "LAP-001"},
        {Name: "足球", Price: 29.99, CategoryID: 2, Stock: 50, SKU: "SPT-001"},
        {Name: "咖啡", Price: 5.99, CategoryID: 3, Stock: 100, SKU: "FOD-001"},
    }
    
    for _, prod := range products {
        if err := db.Create(&prod).Error; err != nil {
            return err
        }
    }
    
    return nil
}
```

## 常见错误避免

1. **未使用事务** - 迁移应为原子操作
2. **忘记记录版本** - 始终记录已应用的迁移
3. **未处理回滚** - 每个迁移都应可逆
4. **未测试迁移** - 始终先在开发环境中测试
5. **未处理错误** - 在每一步都检查错误

## SQLite 特定注意事项

- SQLite 对 `ALTER TABLE` 支持有限
- 复杂的模式变更使用 `db.Exec()`
- 某些操作可能需要重建表
- 注意外键约束

## 调试技巧

1. **启用 GORM 日志**：
```go
db = db.Debug()
```

2. **检查迁移状态**：
```go
var versions []MigrationVersion
db.Find(&versions)
for _, v := range versions {
    fmt.Printf("迁移 %d 在 %s 应用\n", v.Version, v.AppliedAt)
}
```

3. **验证表结构**：
```go
// 检查列是否存在
columns, _ := db.Migrator().ColumnTypes(&Product{})
for _, col := range columns {
    fmt.Printf("列: %s, 类型: %s\n", col.Name(), col.DatabaseTypeName())
}
```

## 性能考虑

1. **批量操作** - 使用事务处理多个操作
2. **索引创建** - 在数据迁移后添加索引
3. **数据验证** - 在迁移前验证数据

## 有用的 GORM 方法

- `db.Begin()` - 开始事务
- `db.Commit()` - 提交事务
- `db.Rollback()` - 回滚事务
- `db.Exec()` - 执行原生 SQL
- `db.Migrator()` - 访问迁移方法
- `db.AutoMigrate()` - 自动迁移模型

## 最终建议

1. **从简单迁移开始** - 先让基本版本追踪正常工作
2. **测试每个迁移** - 在继续之前验证每一步
3. **保持迁移简洁** - 每个迁移应只做一件事
4. **记录你的迁移** - 添加注释说明每个迁移的作用
5. **使用学习资源** - 查阅 GORM 文档中的迁移示例