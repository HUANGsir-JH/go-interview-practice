# 学习 GORM CRUD 操作

## 概述

GORM (Go 对象关系映射器) 是 Go 语言中一个功能强大的 ORM 库，可简化数据库操作。本挑战聚焦于掌握使用 GORM 的基本 CRUD（创建、读取、更新、删除）操作。

## 什么是 GORM？

GORM 是 Go 语言中一个功能丰富的 ORM 库，提供以下特性：
- **自动迁移**：从结构体自动生成数据库表
- **CRUD 操作**：简单的数据库操作方法
- **钩子**：生命周期回调（BeforeCreate、AfterUpdate 等）
- **关联**：处理模型之间的关系
- **验证**：内置验证支持
- **事务**：数据库事务支持

## 基础设置

### 1. 安装
```bash
go get -u gorm.io/gorm
go get -u gorm.io/driver/sqlite  # 用于 SQLite
```

### 2. 数据库连接
```go
import (
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    // 自动迁移模式
    err = db.AutoMigrate(&User{})
    if err != nil {
        return nil, err
    }
    
    return db, nil
}
```

## 定义模型

### 基本模型结构
```go
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"not null"`
    Email     string    `gorm:"unique;not null"`
    Age       int       `gorm:"check:age > 0"`
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

### GORM 标签
- `gorm:"primaryKey"` - 将字段标记为主键
- `gorm:"not null"` - 使字段为必填项
- `gorm:"unique"` - 使字段唯一
- `gorm:"check:condition"` - 添加检查约束
- `gorm:"default:value"` - 设置默认值
- `gorm:"index"` - 在数据库中创建索引

## CRUD 操作

### 1. 创建 (C)
```go
// 创建单个用户
user := User{Name: "John Doe", Email: "john@example.com", Age: 25}
result := db.Create(&user)
if result.Error != nil {
    return result.Error
}

// 创建多个用户
users := []User{
    {Name: "User 1", Email: "user1@example.com", Age: 25},
    {Name: "User 2", Email: "user2@example.com", Age: 30},
}
result = db.Create(&users)
```

### 2. 读取 (R)
```go
// 获取第一个用户
var user User
result := db.First(&user, 1) // 按主键查找
if result.Error != nil {
    return result.Error
}

// 按条件获取用户
var user User
result = db.Where("email = ?", "john@example.com").First(&user)

// 获取所有用户
var users []User
result = db.Find(&users)

// 获取满足条件的用户
var users []User
result = db.Where("age > ?", 18).Find(&users)
```

### 3. 更新 (U)
```go
// 按主键更新
user := User{ID: 1, Name: "Updated Name", Email: "updated@example.com", Age: 30}
result := db.Save(&user)

// 更新特定字段
result = db.Model(&user).Update("Name", "New Name")

// 更新多个字段
result = db.Model(&user).Updates(User{Name: "New Name", Age: 31})

// 按条件更新
result = db.Model(&User{}).Where("age < ?", 18).Update("age", 18)
```

### 4. 删除 (D)
```go
// 按主键删除
result := db.Delete(&User{}, 1)

// 按条件删除
result = db.Where("age < ?", 18).Delete(&User{})

// 软删除（如果模型包含 DeletedAt 字段）
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string
    DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

## 错误处理

### 常见错误模式
```go
// 检查错误
result := db.Create(&user)
if result.Error != nil {
    // 处理错误
    return result.Error
}

// 检查“未找到”错误
if errors.Is(result.Error, gorm.ErrRecordNotFound) {
    // 处理未找到的情况
    return fmt.Errorf("用户不存在")
}

// 检查唯一性约束冲突
if strings.Contains(result.Error.Error(), "UNIQUE constraint failed") {
    // 处理重复条目
    return fmt.Errorf("邮箱已存在")
}
```

## 验证

### 内置验证
```go
type User struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"not null"`
    Email string `gorm:"unique;not null"`
    Age   int    `gorm:"check:age > 0"`
}
```

### 自定义验证
```go
func (u *User) BeforeCreate(tx *gorm.DB) error {
    if u.Age < 0 {
        return fmt.Errorf("年龄不能为负数")
    }
    if !strings.Contains(u.Email, "@") {
        return fmt.Errorf("邮箱格式无效")
    }
    return nil
}
```

## 查询方法

### Where 条件
```go
// 基本 where
db.Where("name = ?", "John").Find(&users)

// 多个条件
db.Where("name = ? AND age > ?", "John", 18).Find(&users)

// IN 条件
db.Where("name IN ?", []string{"John", "Jane"}).Find(&users)

// LIKE 条件
db.Where("name LIKE ?", "%John%").Find(&users)
```

### 排序与限制
```go
// 按某字段排序
db.Order("age DESC").Find(&users)

// 限制数量和偏移
db.Limit(10).Offset(20).Find(&users)

// 选择特定字段
db.Select("name, email").Find(&users)
```

## 事务

### 基本事务
```go
func CreateUserWithProfile(db *gorm.DB, user *User, profile *Profile) error {
    return db.Transaction(func(tx *gorm.DB) error {
        // 创建用户
        if err := tx.Create(user).Error; err != nil {
            return err
        }
        
        // 创建资料
        profile.UserID = user.ID
        if err := tx.Create(profile).Error; err != nil {
            return err
        }
        
        return nil
    })
}
```

### 手动事务
```go
tx := db.Begin()
defer func() {
    if r := recover(); r != nil {
        tx.Rollback()
    }
}()

if err := tx.Create(&user).Error; err != nil {
    tx.Rollback()
    return err
}

if err := tx.Commit().Error; err != nil {
    return err
}
```

## 最佳实践

### 1. 使用指针表示模型
```go
// 正确做法
func GetUser(db *gorm.DB, id uint) (*User, error) {
    var user User
    result := db.First(&user, id)
    return &user, result.Error
}

// 错误做法
func GetUser(db *gorm.DB, id uint) (User, error) {
    var user User
    result := db.First(&user, id)
    return user, result.Error
}
```

### 2. 正确处理错误
```go
// 始终检查错误
result := db.Create(&user)
if result.Error != nil {
    return result.Error
}
```

### 3. 使用合适的查询方法
```go
// 单条记录使用 First()
var user User
db.First(&user, id)

// 多条记录使用 Find()
var users []User
db.Find(&users)

// 顺序无关时使用 Take()
var user User
db.Take(&user)
```

### 4. 优化查询
```go
// 仅选择所需字段
db.Select("id, name").Find(&users)

// 使用预加载处理关联关系
db.Preload("Posts").Find(&users)

// 多个操作使用事务
db.Transaction(func(tx *gorm.DB) error {
    // 多个操作
    return nil
})
```

## 常见模式

### CRUD 服务模式
```go
type UserService struct {
    db *gorm.DB
}

func (s *UserService) Create(user *User) error {
    return s.db.Create(user).Error
}

func (s *UserService) GetByID(id uint) (*User, error) {
    var user User
    err := s.db.First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (s *UserService) Update(user *User) error {
    return s.db.Save(user).Error
}

func (s *UserService) Delete(id uint) error {
    return s.db.Delete(&User{}, id).Error
}
```

### 仓库模式
```go
type UserRepository interface {
    Create(user *User) error
    GetByID(id uint) (*User, error)
    GetAll() ([]User, error)
    Update(user *User) error
    Delete(id uint) error
}

type userRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) UserRepository {
    return &userRepository{db: db}
}
```

## 资源

- [GORM 文档](https://gorm.io/docs/)
- [GORM CRUD 操作](https://gorm.io/docs/create.html)
- [GORM 查询接口](https://gorm.io/docs/query.html)
- [GORM 钩子](https://gorm.io/docs/hooks.html)
- [GORM 事务](https://gorm.io/docs/transactions.html)

## 练习题

1. 创建一个简单的用户管理系统
2. 实现博客文章系统的 CRUD 操作
3. 构建带分类的产品目录
4. 创建一个任务管理应用程序
5. 实现一个简单的库存系统

这些练习将帮助你掌握 GORM 的 CRUD 操作，并理解 Go 应用程序中的数据库交互。