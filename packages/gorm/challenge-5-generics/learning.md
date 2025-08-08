# 学习指南：GORM 泛型 API

## 简介

GORM v1.30.0+ 引入了革命性的泛型 API，提供了类型安全、更好的性能以及更佳的开发者体验。本指南将帮助你理解并掌握基于泛型的数据库操作新方法。

## 为什么使用泛型？

### 传统 API 的问题
```go
// 传统 API - 可能存在的问题
var user User
db.Where("name = ?", name).First(&user) // 缺乏编译时类型检查
// 容易因复用 db 实例导致 SQL 污染
// IDE 支持较弱
```

### 泛型 API 的优势
```go
// 泛型 API - 改进后
user, err := gorm.G[User](db).Where("name = ?", name).First(ctx)
// ✅ 编译时类型安全
// ✅ 更好的性能（减少 SQL 污染）
// ✅ 增强的 IDE 支持
// ✅ 必须使用上下文
```

## 核心概念

### 1. 类型安全操作

`gorm.G[T]` 函数创建一个类型安全的数据库实例：

```go
// 类型安全的用户操作
userDB := gorm.G[User](db)
user, err := userDB.Where("age > ?", 18).First(ctx)

// 类型安全的公司操作  
companyDB := gorm.G[Company](db)
companies, err := companyDB.Find(ctx)
```

### 2. 上下文优先设计

所有泛型操作都需要上下文：

```go
ctx := context.Background()

// 基础操作
user, err := gorm.G[User](db).Create(ctx, &User{Name: "John"})
users, err := gorm.G[User](db).Find(ctx)
user, err := gorm.G[User](db).First(ctx)
err := gorm.G[User](db).Delete(ctx)
```

### 3. 增强的配置

通过额外参数传递配置选项：

```go
// 冲突处理
err := gorm.G[User](db, clause.OnConflict{DoNothing: true}).Create(ctx, &user)

// 执行提示
users, err := gorm.G[User](db, 
    hints.New("USE_INDEX(users, idx_name)"),
).Find(ctx)

// 结果元数据
result := gorm.WithResult()
err := gorm.G[User](db, result).Create(ctx, &user)
fmt.Printf("受影响行数: %d", result.RowsAffected)
```

## CRUD 操作

### 创建操作

```go
// 单条创建
user := &User{Name: "Alice", Email: "alice@example.com", Age: 25}
err := gorm.G[User](db).Create(ctx, user)

// 批量创建
users := []User{
    {Name: "Bob", Email: "bob@example.com", Age: 30},
    {Name: "Charlie", Email: "charlie@example.com", Age: 35},
}
err := gorm.G[User](db).CreateInBatches(ctx, users, 10)
```

### 读取操作

```go
// 条件查询
users, err := gorm.G[User](db).Where("age >= ?", 18).Find(ctx)

// 获取第一条记录
user, err := gorm.G[User](db).Where("email = ?", email).First(ctx)

// 统计记录数
count, err := gorm.G[User](db).Where("age >= ?", 18).Count(ctx)
```

### 更新操作

```go
// 更新单个字段
err := gorm.G[User](db).Where("id = ?", userID).Update(ctx, "age", 26)

// 更新多个字段
err := gorm.G[User](db).Where("id = ?", userID).Updates(ctx, User{
    Name: "更新后的名字",
    Age:  26,
})
```

### 删除操作

```go
// 条件删除
err := gorm.G[User](db).Where("age < ?", 18).Delete(ctx)

// 按 ID 删除
err := gorm.G[User](db).Where("id = ?", userID).Delete(ctx)
```

## 高级功能

### 冲突处理

优雅地处理重复键冲突：

```go
// 冲突时什么都不做
err := gorm.G[User](db, clause.OnConflict{DoNothing: true}).Create(ctx, &user)

// 冲突时更新
err := gorm.G[User](db, clause.OnConflict{
    Columns:   []clause.Column{{Name: "email"}},
    DoUpdates: clause.AssignmentColumns([]string{"name", "age", "updated_at"}),
}).Create(ctx, &user)

// 自定义冲突解决
err := gorm.G[User](db, clause.OnConflict{
    Columns: []clause.Column{{Name: "email"}},
    DoUpdates: clause.Assignments(map[string]interface{}{
        "login_count": gorm.Expr("login_count + 1"),
        "last_login":  time.Now(),
    }),
}).Create(ctx, &user)
```

### 增强的关联查询

更灵活强大的关联查询操作：

```go
// 基础关联查询
users, err := gorm.G[User](db).Joins(clause.InnerJoin.Association("Company"), nil).Find(ctx)

// 带自定义条件的关联查询
users, err := gorm.G[User](db).Joins(clause.LeftJoin.Association("Company"), 
    func(db gorm.JoinBuilder, joinTable clause.Table, curTable clause.Table) error {
        db.Where("companies.industry = ?", "科技")
        db.Where("companies.founded_year > ?", 2000)
        return nil
    }).Find(ctx)

// 子查询关联
users, err := gorm.G[User](db).Joins(
    clause.LeftJoin.AssociationFrom("Company", 
        gorm.G[Company](db).Select("id", "name").Where("active = ?", true)
    ).As("active_companies"),
    func(db gorm.JoinBuilder, joinTable clause.Table, curTable clause.Table) error {
        db.Where("?.industry = ?", joinTable, "科技")
        return nil
    },
).Find(ctx)
```

### 增强的预加载

更精细的关联加载控制：

```go
// 基础预加载
users, err := gorm.G[User](db).Preload("Posts", nil).Find(ctx)

// 带条件的预加载
users, err := gorm.G[User](db).Preload("Posts", func(db gorm.PreloadBuilder) error {
    db.Where("published = ?", true)
    db.Order("created_at DESC")
    return nil
}).Find(ctx)

// 每条记录限制数量
users, err := gorm.G[User](db).Preload("Posts", func(db gorm.PreloadBuilder) error {
    db.Order("created_at DESC").LimitPerRecord(5)
    return nil
}).Find(ctx)

// 嵌套预加载
users, err := gorm.G[User](db).
    Preload("Posts", func(db gorm.PreloadBuilder) error {
        db.Where("published = ?", true)
        return nil
    }).
    Preload("Posts.Comments", func(db gorm.PreloadBuilder) error {
        db.Where("approved = ?", true)
        db.LimitPerRecord(3)
        return nil
    }).Find(ctx)
```

## 性能优化

### 批量操作

```go
// 高效批量插入
users := make([]User, 1000)
// ... 填充 users
err := gorm.G[User](db).CreateInBatches(ctx, users, 100)

// 批量更新
err := gorm.G[User](db).Where("department = ?", "工程部").Updates(ctx, map[string]interface{}{
    "bonus": gorm.Expr("salary * 0.1"),
})
```

### 查询优化

```go
// 选择特定字段
users, err := gorm.G[User](db).Select("id", "name", "email").Find(ctx)

// 有效使用索引
users, err := gorm.G[User](db, 
    hints.New("USE_INDEX(users, idx_email)"),
).Where("email LIKE ?", "%@company.com").Find(ctx)
```

### 连接池管理

```go
// 带超时的上下文
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

users, err := gorm.G[User](db).Find(ctx)
if err != nil {
    if errors.Is(err, context.DeadlineExceeded) {
        // 处理超时
    }
}
```

## 从传统 API 迁移

### 迁移前（传统 API）
```go
func GetActiveUsers(db *gorm.DB) ([]User, error) {
    var users []User
    err := db.Where("active = ?", true).Find(&users).Error
    return users, err
}

func CreateUser(db *gorm.DB, user *User) error {
    return db.Create(user).Error
}
```

### 迁移后（泛型 API）
```go
func GetActiveUsers(ctx context.Context, db *gorm.DB) ([]User, error) {
    return gorm.G[User](db).Where("active = ?", true).Find(ctx)
}

func CreateUser(ctx context.Context, db *gorm.DB, user *User) error {
    return gorm.G[User](db).Create(ctx, user)
}
```

## 错误处理

### 上下文感知的错误处理

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

user, err := gorm.G[User](db).Where("id = ?", id).First(ctx)
if err != nil {
    switch {
    case errors.Is(err, context.DeadlineExceeded):
        return nil, fmt.Errorf("查询超时: %w", err)
    case errors.Is(err, context.Canceled):
        return nil, fmt.Errorf("查询被取消: %w", err)
    case errors.Is(err, gorm.ErrRecordNotFound):
        return nil, fmt.Errorf("用户未找到: %w", err)
    default:
        return nil, fmt.Errorf("数据库错误: %w", err)
    }
}
```

## 最佳实践

### 1. 始终使用上下文
```go
// ✅ 良好做法 - 始终传递上下文
ctx := context.Background()
users, err := gorm.G[User](db).Find(ctx)

// ❌ 不良做法 - 传统 API 仍可用但失去优势
var users []User
db.Find(&users)
```

### 2. 利用类型安全
```go
// ✅ 良好做法 - 类型安全操作
user, err := gorm.G[User](db).Where("age > ?", 18).First(ctx)

// ✅ 良好做法 - 编译时类型检查
users, err := gorm.G[User](db).Where("company_id = ?", companyID).Find(ctx)
```

### 3. 使用增强功能
```go
// ✅ 良好做法 - 使用 OnConflict 实现 upsert
err := gorm.G[User](db, clause.OnConflict{
    Columns:   []clause.Column{{Name: "email"}},
    DoUpdates: clause.AssignmentColumns([]string{"name", "updated_at"}),
}).Create(ctx, &user)

// ✅ 良好做法 - 使用 LimitPerRecord 实现高效预加载
users, err := gorm.G[User](db).Preload("Posts", func(db gorm.PreloadBuilder) error {
    db.Order("created_at DESC").LimitPerRecord(5)
    return nil
}).Find(ctx)
```

### 4. 正确处理错误
```go
// ✅ 良好做法 - 全面的错误处理
user, err := gorm.G[User](db).Where("id = ?", id).First(ctx)
if err != nil {
    if errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, ErrUserNotFound
    }
    return nil, fmt.Errorf("获取用户失败: %w", err)
}
```

## 常见模式

### 使用泛型的仓库模式

```go
type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    return gorm.G[User](r.db).Create(ctx, user)
}

func (r *UserRepository) GetByID(ctx context.Context, id uint) (*User, error) {
    return gorm.G[User](r.db).Where("id = ?", id).First(ctx)
}

func (r *UserRepository) GetActiveUsers(ctx context.Context) ([]User, error) {
    return gorm.G[User](r.db).Where("active = ?", true).Find(ctx)
}
```

### 使用泛型的服务层

```go
type UserService struct {
    repo *UserRepository
}

func (s *UserService) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
    user := &User{
        Name:  req.Name,
        Email: req.Email,
        Age:   req.Age,
    }
    
    err := s.repo.Create(ctx, user)
    if err != nil {
        return nil, fmt.Errorf("创建用户失败: %w", err)
    }
    
    return user, nil
}
```

## 总结

GORM 的泛型 API 代表了 Go ORM 设计的重大演进：

- **类型安全**：编译时类型检查防止运行时错误
- **性能**：减少 SQL 污染并提升连接复用效率
- **开发者体验**：增强的 IDE 支持和更简洁的 API
- **现代模式**：上下文优先设计与增强的错误处理
- **向后兼容**：可与传统 API 共存

在新项目中开始使用泛型 API，亲身体验这些优势！