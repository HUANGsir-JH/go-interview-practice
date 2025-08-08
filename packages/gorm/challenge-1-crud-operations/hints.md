# GORM CRUD 操作挑战提示

## 提示 1：数据库连接设置

从数据库连接开始——确保你的 `ConnectDB()` 函数正确连接到 SQLite，并自动迁移 User 模型。

使用 `gorm.Open()` 配合 SQLite 驱动，调用 `AutoMigrate(&User{})` 创建表，并返回数据库连接和任何错误。

```go
import "gorm.io/driver/sqlite"

func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    err = db.AutoMigrate(&User{})
    return db, err
}
```

## 提示 2：创建用户

使用 `db.Create(user)` 插入用户。操作后检查错误。创建后用户的 ID 将自动设置。

```go
func CreateUser(db *gorm.DB, user *User) error {
    result := db.Create(user)
    return result.Error
}
```

## 提示 3：按 ID 读取用户

使用 `db.First(&user, id)` 按 ID 查找用户。处理用户不存在的情况并返回用户指针。

```go
func GetUserByID(db *gorm.DB, id uint) (*User, error) {
    var user User
    result := db.First(&user, id)
    if result.Error != nil {
        return nil, result.Error
    }
    return &user, nil
}
```

## 提示 4：读取所有用户

使用 `db.Find(&users)` 获取所有用户。返回用户切片并处理空结果（返回空切片，而不是 nil）。

```go
func GetAllUsers(db *gorm.DB) ([]User, error) {
    var users []User
    result := db.Find(&users)
    return users, result.Error
}
```

## 提示 5：更新用户

使用 `db.Save(user)` 更新用户。确保用户具有有效 ID，并处理用户不存在的情况。

```go
func UpdateUser(db *gorm.DB, user *User) error {
    result := db.Save(user)
    return result.Error
}
```

## 提示 6：删除用户

使用 `db.Delete(&User{}, id)` 按 ID 删除。处理用户不存在的情况并返回适当的错误信息。

```go
func DeleteUser(db *gorm.DB, id uint) error {
    result := db.Delete(&User{}, id)
    return result.Error
}
```

## 常见模式

### 数据库连接
```go
func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    err = db.AutoMigrate(&User{})
    if err != nil {
        return nil, err
    }
    
    return db, nil
}
```

### 错误处理
```go
func CreateUser(db *gorm.DB, user *User) error {
    result := db.Create(user)
    if result.Error != nil {
        return result.Error
    }
    return nil
}
```

### 未找到处理
```go
func GetUserByID(db *gorm.DB, id uint) (*User, error) {
    var user User
    result := db.First(&user, id)
    if result.Error != nil {
        return nil, result.Error
    }
    return &user, nil
}
```

## 验证与约束

### 模型验证
你的 User 模型有以下约束：
- `Name`：必需（非空）
- `Email`：必需且唯一
- `Age`：必须大于 0

### 测试验证
测试将检查：
- 使用无效年龄（负数）创建用户
- 使用重复邮箱创建用户
- 所有 CRUD 操作均能正常工作

## 常见错误避免

1. **未处理错误** - 数据库操作后始终检查错误
2. **返回 nil 而非空切片** - 对于 `GetAllUsers()`，如果没有用户则返回空切片
3. **未检查用户是否存在** - 对于更新/删除操作，先确认用户存在
4. **忘记自动迁移** - 确保在 `ConnectDB()` 中调用 `AutoMigrate()`
5. **未使用指针** - 返回 User 结构体的指针，而非值

## 测试技巧

1. **测试后清理** - 始终清理测试数据
2. **测试边界情况** - 测试无效数据、不存在的用户等
3. **验证约束** - 确保验证逻辑正确

## 调试

1. **启用 GORM 日志** 以查看 SQL 查询：
```go
db = db.Debug()
```

2. **检查迁移后的表结构**：
```go
// 验证表是否存在
assert.True(t, db.Migrator().HasTable(&User{}))
```

3. **检查数据库中的数据**：
```go
// 打印所有用户
var users []User
db.Find(&users)
for _, user := range users {
    fmt.Printf("User: %+v\n", user)
}
```

## 性能考虑

1. **使用适当的方法** - 单条记录使用 `First()`，多条记录使用 `Find()`
2. **处理大数据集** - 对于大结果集考虑分页
3. **使用事务** - 对于多个相关操作

## 有用的 GORM 方法

- `db.Create()` - 创建记录
- `db.First()` - 获取第一条记录
- `db.Find()` - 获取多条记录
- `db.Save()` - 更新记录
- `db.Delete()` - 删除记录
- `db.Where()` - 过滤结果
- `db.AutoMigrate()` - 迁移模型

## SQLite 特定注意事项

- 本挑战使用 SQLite，因此某些 SQL 语法可能与其他数据库不同
- SQLite 对所有基本操作都有良好支持
- 使用 `gorm.io/driver/sqlite` 作为驱动

## 最终建议

1. **仔细阅读测试** - 它们明确展示了你的函数应如何工作
2. **从简单开始** - 先实现基本的 CRUD，再添加验证
3. **逐步测试** - 实现每个函数后立即测试
4. **利用学习资源** - 查阅 GORM 文档获取详细示例

## 常见错误消息

- `UNIQUE constraint failed` - 邮箱已存在
- `CHECK constraint failed` - 年龄无效
- `record not found` - 用户不存在
- `database is locked` - SQLite 文件访问问题

## 代码结构示例

```go
package main

import (
    "time"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"not null"`
    Email     string    `gorm:"unique;not null"`
    Age       int       `gorm:"check:age > 0"`
    CreatedAt time.Time
    UpdatedAt time.Time
}

func ConnectDB() (*gorm.DB, error) {
    // TODO: 实现数据库连接
    return nil, nil
}

func CreateUser(db *gorm.DB, user *User) error {
    // TODO: 实现用户创建
    return nil
}

// ... 其他函数
```

记得逐步实现每个函数并彻底测试！