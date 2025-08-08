# GORM 泛型 API 挑战提示

## 提示 1：数据库连接与迁移

设置数据库连接并迁移所有模型。使用 SQLite 驱动程序并自动迁移三个模型：

```go
import "gorm.io/driver/sqlite"

func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    err = db.AutoMigrate(&User{}, &Company{}, &Post{})
    return db, err
}
```

## 提示 2：基本泛型 CRUD 操作

使用 `gorm.G[T]` 实现类型安全操作。所有泛型操作都需要上下文：

```go
func CreateUser(ctx context.Context, db *gorm.DB, user *User) error {
    return gorm.G[User](db).Create(ctx, user)
}

func GetUserByID(ctx context.Context, db *gorm.DB, id uint) (*User, error) {
    return gorm.G[User](db).Where("id = ?", id).First(ctx)
}

func UpdateUserAge(ctx context.Context, db *gorm.DB, userID uint, age int) error {
    return gorm.G[User](db).Where("id = ?", userID).Update(ctx, "age", age)
}

func DeleteUser(ctx context.Context, db *gorm.DB, userID uint) error {
    return gorm.G[User](db).Where("id = ?", userID).Delete(ctx)
}
```

## 提示 3：批量操作与范围查询

使用 `CreateInBatches` 实现高效批量操作，使用范围条件进行查询：

```go
func CreateUsersInBatches(ctx context.Context, db *gorm.DB, users []User, batchSize int) error {
    return gorm.G[User](db).CreateInBatches(ctx, users, batchSize)
}

func FindUsersByAgeRange(ctx context.Context, db *gorm.DB, minAge, maxAge int) ([]User, error) {
    return gorm.G[User](db).Where("age BETWEEN ? AND ?", minAge, maxAge).Find(ctx)
}
```

## 提示 4：冲突处理与结果元数据

使用 `clause.OnConflict` 处理 upsert 操作，并使用 `gorm.WithResult()` 捕获元数据：

```go
func UpsertUser(ctx context.Context, db *gorm.DB, user *User) error {
    return gorm.G[User](db, clause.OnConflict{
        Columns:   []clause.Column{{Name: "email"}},
        DoUpdates: clause.AssignmentColumns([]string{"name", "age"}),
    }).Create(ctx, user)
}

func CreateUserWithResult(ctx context.Context, db *gorm.DB, user *User) (int64, error) {
    result := gorm.WithResult()
    err := gorm.G[User](db, result).Create(ctx, user)
    if err != nil {
        return 0, err
    }
    return result.RowsAffected, nil
}
```

## 提示 5：增强的关联查询与自定义条件

使用新的关联语法配合自定义过滤函数：

```go
func GetUsersWithCompany(ctx context.Context, db *gorm.DB) ([]User, error) {
    return gorm.G[User](db).Joins(clause.InnerJoin.Association("Company"), nil).Find(ctx)
}

func SearchUsersInCompany(ctx context.Context, db *gorm.DB, companyName string) ([]User, error) {
    return gorm.G[User](db).Joins(clause.InnerJoin.Association("Company"), 
        func(db gorm.JoinBuilder, joinTable clause.Table, curTable clause.Table) error {
            db.Where("companies.name = ?", companyName)
            return nil
        }).Find(ctx)
}
```

## 提示 6：带限制的增强预加载

使用新的预加载语法配合 `LimitPerRecord` 和自定义条件：

```go
func GetUsersWithPosts(ctx context.Context, db *gorm.DB, limit int) ([]User, error) {
    return gorm.G[User](db).Preload("Posts", func(db gorm.PreloadBuilder) error {
        db.Order("created_at DESC").LimitPerRecord(limit)
        return nil
    }).Find(ctx)
}

func GetUserWithPostsAndCompany(ctx context.Context, db *gorm.DB, userID uint) (*User, error) {
    return gorm.G[User](db).
        Preload("Posts", func(db gorm.PreloadBuilder) error {
            db.Order("created_at DESC")
            return nil
        }).
        Preload("Company", nil).
        Where("id = ?", userID).First(ctx)
}
```

## 提示 7：带聚合的复杂查询

结合关联、分组和排序实现复杂的分析查询：

```go
func GetTopActiveUsers(ctx context.Context, db *gorm.DB, limit int) ([]User, error) {
    return gorm.G[User](db).
        Joins("LEFT JOIN posts ON users.id = posts.user_id").
        Group("users.id").
        Order("COUNT(posts.id) DESC").
        Limit(limit).
        Find(ctx)
}
```

## 提示 8：上下文模式与错误处理

始终正确使用上下文并处理泛型特有的错误：

```go
// 为数据库操作创建带超时的上下文
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

// 处理上下文取消
user, err := gorm.G[User](db).Where("id = ?", id).First(ctx)
if err != nil {
    if errors.Is(err, context.Canceled) {
        return nil, errors.New("操作已被取消")
    }
    if errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, errors.New("用户未找到")
    }
    return nil, err
}
```

## 与传统 API 的主要区别

**传统 API：**
```go
var user User
db.Where("name = ?", name).First(&user)
```

**泛型 API：**
```go
user, err := gorm.G[User](db).Where("name = ?", name).First(ctx)
```

**优势：**
- 编译时类型安全
- 更佳性能（减少 SQL 污染）
- 更清晰的错误处理
- 必须使用上下文
- 更强的 IDE 支持