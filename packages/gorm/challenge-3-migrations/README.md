# 挑战 3：数据库迁移

使用 GORM 构建一个 **电子商务系统**，以展示数据库迁移、模式演进和数据库变更的版本控制。

## 挑战要求

创建一个 Go 应用程序，实现以下功能：

1. **数据库迁移** - 受版本控制的模式变更
2. **模式演进** - 添加、修改和删除数据库结构
3. **迁移回滚** - 能够撤销模式变更
4. **数据填充** - 使用初始数据填充数据库

## 数据模型

```go
// 版本 1：基础产品系统
type Product struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"not null"`
    Price       float64   `gorm:"not null"`
    Description string    `gorm:"type:text"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

// 版本 2：添加分类
type Category struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"unique;not null"`
    Description string    `gorm:"type:text"`
    Products    []Product `gorm:"foreignKey:CategoryID"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

// 版本 3：增强版产品，包含库存信息
type Product struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"not null"`
    Price       float64   `gorm:"not null"`
    Description string    `gorm:"type:text"`
    CategoryID  uint      `gorm:"not null"`
    Category    Category  `gorm:"foreignKey:CategoryID"`
    Stock       int       `gorm:"default:0"`
    SKU         string    `gorm:"unique;not null"`
    IsActive    bool      `gorm:"default:true"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}
```

## 必需函数

实现以下函数：
- `ConnectDB() (*gorm.DB, error)` - 数据库连接
- `RunMigration(db *gorm.DB, version int) error` - 运行指定版本的迁移
- `RollbackMigration(db *gorm.DB, version int) error` - 回滚到指定版本
- `GetMigrationVersion(db *gorm.DB) (int, error)` - 获取当前迁移版本
- `SeedData(db *gorm.DB) error` - 使用初始数据填充数据库
- `CreateProduct(db *gorm.DB, product *Product) error` - 创建产品并进行验证
- `GetProductsByCategory(db *gorm.DB, categoryID uint) ([]Product, error)` - 根据分类获取产品
- `UpdateProductStock(db *gorm.DB, productID uint, quantity int) error` - 更新产品库存

## 迁移版本

**版本 1**：创建基础的产品表  
**版本 2**：添加分类表及外键关系  
**版本 3**：在产品中添加库存字段（stock、SKU、is_active）

## 测试要求

你的解决方案必须通过以下测试：
- 顺序运行迁移
- 回滚迁移
- 追踪迁移版本
- 填充初始数据
- 创建带分类关系的产品
- 根据分类查询产品
- 更新产品库存
- 处理迁移冲突和错误