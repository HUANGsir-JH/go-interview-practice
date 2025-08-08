# 挑战 2：关联与关系

使用 GORM 构建一个 **博客系统**，以展示模型之间的数据库关系和关联。

## 挑战要求

创建一个 Go 应用程序，实现以下功能：

1. **一对多关系** - 用户可以拥有多个文章
2. **多对多关系** - 文章可以有多个标签
3. **关联操作** - 创建、查询和管理相关数据
4. **预加载** - 高效地加载相关数据

## 数据模型

```go
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"not null"`
    Email     string    `gorm:"unique;not null"`
    Posts     []Post    `gorm:"foreignKey:UserID"`
    CreatedAt time.Time
    UpdatedAt time.Time
}

type Post struct {
    ID          uint      `gorm:"primaryKey"`
    Title       string    `gorm:"not null"`
    Content     string    `gorm:"type:text"`
    UserID      uint      `gorm:"not null"`
    User        User      `gorm:"foreignKey:UserID"`
    Tags        []Tag     `gorm:"many2many:post_tags;"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

type Tag struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"unique;not null"`
    Posts []Post `gorm:"many2many:post_tags;"`
}
```

## 必需函数

实现以下函数：
- `ConnectDB() (*gorm.DB, error)` - 数据库连接并自动迁移
- `CreateUserWithPosts(db *gorm.DB, user *User) error` - 创建用户及其文章
- `GetUserWithPosts(db *gorm.DB, userID uint) (*User, error)` - 获取用户及其文章
- `CreatePostWithTags(db *gorm.DB, post *Post, tagNames []string) error` - 创建文章并添加标签
- `GetPostsByTag(db *gorm.DB, tagName string) ([]Post, error)` - 根据标签获取文章
- `AddTagsToPost(db *gorm.DB, postID uint, tagNames []string) error` - 为已有文章添加标签
- `GetPostWithUserAndTags(db *gorm.DB, postID uint) (*Post, error)` - 获取文章及其作者和标签

## 测试要求

你的解决方案必须通过以下测试：
- 创建带有相关文章的用户
- 创建包含多个标签的文章
- 查询用户及其文章（预加载）
- 根据标签查询文章
- 为已有文章添加标签
- 加载文章及其作者和标签关联
- 正确的外键约束和关系