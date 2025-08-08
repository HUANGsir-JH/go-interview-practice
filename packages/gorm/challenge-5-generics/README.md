# 挑战 5：泛型方式

使用 GORM 的新泛型 API（v1.30.0+）构建一个**现代用户与文章管理系统**，展示类型安全的数据库操作和增强功能。

## 挑战要求

创建一个 Go 应用程序，利用 GORM 的泛型 API 实现：

1. **上下文感知操作** - 所有操作均使用上下文以获得更好的控制
2. **类型安全的 CRUD** - 使用 `gorm.G[T]` 实现类型安全并减少 SQL 污染
3. **增强的关联查询与预加载** - 使用新 API 处理高级关联关系
4. **高级功能** - 支持 OnConflict 处理、执行提示和结果元数据
5. **性能优化** - 批量操作和连接管理

## 数据模型

```go
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"not null"`
    Email     string    `gorm:"unique;not null"`
    Age       int       `gorm:"check:age > 0"`
    CompanyID *uint     `gorm:"index"`
    Company   *Company  `gorm:"foreignKey:CompanyID"`
    Posts     []Post    `gorm:"foreignKey:UserID"`
    CreatedAt time.Time
    UpdatedAt time.Time
}

type Company struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"not null;unique"`
    Industry    string    `gorm:"not null"`
    FoundedYear int       `gorm:"not null"`
    Users       []User    `gorm:"foreignKey:CompanyID"`
    CreatedAt   time.Time
}

type Post struct {
    ID        uint      `gorm:"primaryKey"`
    Title     string    `gorm:"not null"`
    Content   string    `gorm:"type:text"`
    UserID    uint      `gorm:"not null;index"`
    User      User      `gorm:"foreignKey:UserID"`
    ViewCount int       `gorm:"default:0"`
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

## 必需函数

使用 GORM 的泛型 API 实现以下函数：

### 基础操作
- `ConnectDB() (*gorm.DB, error)` - 数据库连接并自动迁移
- `CreateUser(ctx context.Context, db *gorm.DB, user *User) error` - 使用泛型创建用户
- `GetUserByID(ctx context.Context, db *gorm.DB, id uint) (*User, error)` - 根据 ID 获取用户
- `UpdateUserAge(ctx context.Context, db *gorm.DB, userID uint, age int) error` - 更新特定字段
- `DeleteUser(ctx context.Context, db *gorm.DB, userID uint) error` - 删除用户

### 批量操作
- `CreateUsersInBatches(ctx context.Context, db *gorm.DB, users []User, batchSize int) error` - 批量创建
- `FindUsersByAgeRange(ctx context.Context, db *gorm.DB, minAge, maxAge int) ([]User, error)` - 范围查询

### 高级功能
- `UpsertUser(ctx context.Context, db *gorm.DB, user *User) error` - 处理冲突
- `CreateUserWithResult(ctx context.Context, db *gorm.DB, user *User) (int64, error)` - 返回元数据

### 增强的关联查询
- `GetUsersWithCompany(ctx context.Context, db *gorm.DB) ([]User, error)` - 增强的关联查询
- `GetUsersWithPosts(ctx context.Context, db *gorm.DB, limit int) ([]User, error)` - 带限制的预加载
- `GetUserWithPostsAndCompany(ctx context.Context, db *gorm.DB, userID uint) (*User, error)` - 多重预加载

### 复杂查询
- `SearchUsersInCompany(ctx context.Context, db *gorm.DB, companyName string) ([]User, error)` - 关联查询带过滤条件
- `GetTopActiveUsers(ctx context.Context, db *gorm.DB, limit int) ([]User, error)` - 文章数量最多的用户

## 需要展示的关键泛型特性

### 1. 类型安全操作
```go
// 不再是：db.Where("name = ?", name).First(&user)
user, err := gorm.G[User](db).Where("name = ?", name).First(ctx)
```

### 2. 上下文支持
```go
// 所有操作都需要上下文
ctx := context.Background()
users, err := gorm.G[User](db).Find(ctx)
```

### 3. OnConflict 处理
```go
// 处理主键冲突
err := gorm.G[User](db, clause.OnConflict{DoNothing: true}).Create(ctx, &user)
```

### 4. 增强的关联查询
```go
// 更灵活的关联条件
users, err := gorm.G[User](db).Joins(clause.LeftJoin.Association("Company"), 
    func(db gorm.JoinBuilder, joinTable clause.Table, curTable clause.Table) error {
        db.Where("companies.industry = ?", "Technology")
        return nil
    }).Find(ctx)
```

### 5. 预加载增强
```go
// 每条记录限制数量及自定义条件
users, err := gorm.G[User](db).Preload("Posts", func(db gorm.PreloadBuilder) error {
    db.Order("created_at DESC").LimitPerRecord(3)
    return nil
}).Find(ctx)
```

## 测试要求

你的解决方案必须通过以下测试：
- 上下文感知的数据库操作
- 使用泛型实现的类型安全 CRUD 操作
- 批量操作及性能优化
- 重复数据的 OnConflict 处理
- 带自定义条件的增强关联查询
- 带限制和过滤的高级预加载
- 结合多种特性的复杂查询
- 正确的错误处理和上下文取消

## 性能优势

泛型 API 提供了：
- **类型安全** - 编译时类型检查
- **减少 SQL 污染** - 更好的连接复用
- **性能提升** - 优化的查询构建
- **更好的工具支持** - IDE 支持和自动补全

## 从传统 API 迁移

如果需要迁移现有代码：
```go
// 传统 API
var user User
db.Where("id = ?", id).First(&user)

// 泛型 API
user, err := gorm.G[User](db).Where("id = ?", id).First(ctx)
```

## 要求

- Go 1.18+（支持泛型）
- GORM v1.30.0+（支持泛型 API）
- 上下文感知编程模式

开始实现，体验 GORM 泛型 API 带来的更优类型安全和性能！ 🚀