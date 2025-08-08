# 挑战 1：CRUD 操作

使用 GORM 构建一个 **用户管理系统**，展示基本的数据库操作。

## 挑战要求

创建一个支持以下功能的 Go 应用程序：

1. **创建** - 将新用户添加到数据库
2. **读取** - 查询并检索用户
3. **更新** - 修改现有用户数据
4. **删除** - 从数据库中移除用户
5. **数据库连接** - 连接到 SQLite 数据库

## 数据模型

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

## 必需函数

实现以下函数：
- `ConnectDB() (*gorm.DB, error)` - 数据库连接
- `CreateUser(db *gorm.DB, user *User) error` - 创建用户
- `GetUserByID(db *gorm.DB, id uint) (*User, error)` - 获取用户
- `GetAllUsers(db *gorm.DB) ([]User, error)` - 获取所有用户
- `UpdateUser(db *gorm.DB, user *User) error` - 更新用户
- `DeleteUser(db *gorm.DB, id uint) error` - 删除用户

## 测试要求

你的解决方案必须通过以下测试：
- 数据库连接和表创建
- 带验证的用户创建
- 通过 ID 查询用户并获取所有用户
- 更新用户信息
- 从数据库中删除用户
- 无效操作的错误处理