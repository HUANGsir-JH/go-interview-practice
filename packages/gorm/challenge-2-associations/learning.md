# 学习 GORM 关联关系

## 概述

GORM 关联关系允许您定义不同模型之间的关系，从而轻松处理相关数据。本挑战重点在于理解和实现 GORM 中的各种关联类型。

## 关联类型

### 1. 一对一
一种一对一关系，其中一个表中的每条记录仅与另一个表中的一条记录相关联。

```go
type User struct {
    ID       uint   `gorm:"primaryKey"`
    Name     string
    Profile  Profile `gorm:"foreignKey:UserID"`
}

type Profile struct {
    ID     uint   `gorm:"primaryKey"`
    UserID uint   `gorm:"unique"`
    Bio    string
}
```

### 2. 一对多
一种一对多关系，其中一条记录可以与另一张表中的多条记录相关联。

```go
type User struct {
    ID    uint    `gorm:"primaryKey"`
    Name  string
    Posts []Post  `gorm:"foreignKey:UserID"`
}

type Post struct {
    ID     uint   `gorm:"primaryKey"`
    Title  string
    UserID uint
    User   User   `gorm:"foreignKey:UserID"`
}
```

### 3. 多对多
一种多对多关系，其中多个记录可以与另一个表中的多个记录相关联。

```go
type Post struct {
    ID    uint   `gorm:"primaryKey"`
    Title string
    Tags  []Tag  `gorm:"many2many:post_tags;"`
}

type Tag struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string
    Posts []Post `gorm:"many2many:post_tags;"`
}
```

## 核心概念

### 外键
- 使用 `gorm:"foreignKey:FieldName"` 来指定外键字段
- 外键应引用相关模型的主键
- GORM 自动处理外键约束

### 预加载
预加载可高效加载相关数据：

```go
// 加载用户及其文章
var user User
db.Preload("Posts").First(&user, userID)

// 加载文章及其作者和标签
var post Post
db.Preload("User").Preload("Tags").First(&post, postID)
```

### 关联模式
GORM 提供了不同的关联模式来创建相关记录：

```go
// 创建用户及其文章
user := User{
    Name: "John",
    Posts: []Post{
        {Title: "第一篇文章"},
        {Title: "第二篇文章"},
    },
}
db.Create(&user) // 在事务中创建用户和文章
```

## 最佳实践

### 1. 为性能使用预加载
当需要相关数据时，请始终使用预加载以避免 N+1 查询问题：

```go
// 良好：单次查询配合预加载
var users []User
db.Preload("Posts").Find(&users)

// 不良：N+1 查询
var users []User
db.Find(&users)
for _, user := range users {
    db.Model(&user).Association("Posts").Find(&user.Posts)
}
```

### 2. 处理关联错误
在操作关联时始终检查错误：

```go
if err := db.Create(&user).Error; err != nil {
    // 处理错误
}
```

### 3. 对复杂操作使用事务
在创建多个相关记录时使用事务：

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

## 常见模式

### 创建相关记录
```go
// 方法 1：使用关联模式
user := User{Name: "John"}
post := Post{Title: "我的文章", User: user}
db.Create(&post)

// 方法 2：使用关联
user := User{Name: "John"}
db.Create(&user)
post := Post{Title: "我的文章"}
db.Model(&user).Association("Posts").Append(&post)
```

### 查询相关数据
```go
// 获取带有文章的用户
var user User
db.Preload("Posts").First(&user, userID)

// 获取某个用户的全部文章
var posts []Post
db.Where("user_id = ?", userID).Find(&posts)

// 获取拥有文章的用户
var users []User
db.Preload("Posts").Where("EXISTS (SELECT 1 FROM posts WHERE posts.user_id = users.id)").Find(&users)
```

### 更新关联
```go
// 替换用户的全部文章
db.Model(&user).Association("Posts").Replace([]Post{
    {Title: "新文章 1"},
    {Title: "新文章 2"},
})

// 向用户添加文章
db.Model(&user).Association("Posts").Append(&Post{Title: "新文章"})

// 从用户移除文章
db.Model(&user).Association("Posts").Delete(&Post{Title: "旧文章"})
```

## 高级功能

### 多态关联
GORM 支持多态关联以处理更复杂的关联关系：

```go
type Comment struct {
    ID        uint   `gorm:"primaryKey"`
    Content   string
    UserID    uint
    User      User
    CommentableType string
    CommentableID   uint
}

type Post struct {
    ID       uint      `gorm:"primaryKey"`
    Title    string
    Comments []Comment `gorm:"polymorphic:Commentable;"`
}
```

### 自引用关联
用于层次化数据结构：

```go
type Category struct {
    ID       uint       `gorm:"primaryKey"`
    Name     string
    ParentID *uint
    Parent   *Category  `gorm:"foreignKey:ParentID"`
    Children []Category `gorm:"foreignKey:ParentID"`
}
```

## 资源

- [GORM 关联文档](https://gorm.io/docs/associations.html)
- [GORM 预加载](https://gorm.io/docs/preload.html)
- [GORM 多对多](https://gorm.io/docs/many_to_many.html)
- [GORM 多态关联](https://gorm.io/docs/polymorphic_association.html)

## 练习题

1. 创建一个包含用户、文章和评论的博客系统  
2. 实现一个带分类和标签的产品目录  
3. 构建一个包含用户、文章和点赞功能的社交网络  
4. 创建一个电商系统，包含订单、商品和客户  

这些练习将帮助您掌握 GORM 关联关系，并理解如何设计有效的数据库关系。