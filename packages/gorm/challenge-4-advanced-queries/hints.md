# GORM 高级查询挑战提示

## 提示 1：数据库连接与数据模型

本挑战涉及用户、帖子和点赞之间的复杂关系。使用 `gorm.Open()` 连接 SQLite 数据库，并自动迁移所有模型：

```go
func ConnectDB() (*gorm.DB, error) {
    db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    err = db.AutoMigrate(&User{}, &Post{}, &Like{})
    return db, err
}
```

## 提示 2：按发帖数量排序的顶级用户

使用聚合函数结合连接、分组和排序：

```go
func GetTopUsersByPostCount(db *gorm.DB, limit int) ([]User, error) {
    var users []User
    err := db.Joins("LEFT JOIN posts ON users.id = posts.user_id").
        Group("users.id").
        Order("COUNT(posts.id) DESC").
        Limit(limit).
        Find(&users).Error
    return users, err
}
```

## 提示 3：按类别获取帖子并分页

使用 `Where()` 进行筛选，`Preload()` 加载用户信息，并实现分页功能：

```go
func GetPostsByCategoryWithUserInfo(db *gorm.DB, category string, page, pageSize int) ([]Post, int64, error) {
    var posts []Post
    var total int64
    
    query := db.Where("category = ?", category)
    query.Model(&Post{}).Count(&total)
    
    offset := (page - 1) * pageSize
    err := query.Preload("User").Offset(offset).Limit(pageSize).Find(&posts).Error
    
    return posts, total, err
}
```

## 提示 4：用户参与度统计

在一个函数中使用不同的查询方法计算多个指标：

```go
func GetUserEngagementStats(db *gorm.DB, userID uint) (map[string]interface{}, error) {
    stats := make(map[string]interface{})
    
    // 发帖数量
    var postCount int64
    db.Model(&Post{}).Where("user_id = ?", userID).Count(&postCount)
    stats["post_count"] = postCount
    
    // 收到的点赞数
    var likesReceived int64
    db.Model(&Like{}).Joins("JOIN posts ON likes.post_id = posts.id").
        Where("posts.user_id = ?", userID).Count(&likesReceived)
    stats["likes_received"] = likesReceived
    
    // 平均浏览量
    var avgViews float64
    db.Model(&Post{}).Select("AVG(view_count)").Where("user_id = ?", userID).Scan(&avgViews)
    stats["average_views"] = avgViews
    
    return stats, nil
}
```

## 提示 5：指定时间段内按点赞数排序的热门帖子

使用连接配合时间过滤和聚合：

```go
func GetPopularPostsByLikes(db *gorm.DB, days int, limit int) ([]Post, error) {
    var posts []Post
    cutoffDate := time.Now().AddDate(0, 0, -days)
    
    err := db.Joins("LEFT JOIN likes ON posts.id = likes.post_id").
        Where("posts.created_at >= ?", cutoffDate).
        Group("posts.id").
        Order("COUNT(likes.id) DESC").
        Limit(limit).
        Find(&posts).Error
    
    return posts, err
}
```

## 提示 6：按国家划分的用户统计

使用 `Select()` 搭配聚合函数和 `Group()`：

```go
func GetCountryUserStats(db *gorm.DB) ([]map[string]interface{}, error) {
    var results []struct {
        Country   string
        UserCount int64
        AvgAge    float64
    }
    
    err := db.Model(&User{}).
        Select("country, COUNT(*) as user_count, AVG(age) as avg_age").
        Group("country").
        Scan(&results).Error
    
    var stats []map[string]interface{}
    for _, result := range results {
        stat := map[string]interface{}{
            "country":    result.Country,
            "user_count": result.UserCount,
            "avg_age":    result.AvgAge,
        }
        stats = append(stats, stat)
    }
    
    return stats, err
}
```

## 提示 7：按内容搜索帖子

使用 `Where()` 和 `LIKE` 操作符对多个字段进行搜索：

```go
func SearchPostsByContent(db *gorm.DB, query string, limit int) ([]Post, error) {
    var posts []Post
    searchPattern := "%" + query + "%"
    
    err := db.Where("title LIKE ? OR content LIKE ?", searchPattern, searchPattern).
        Limit(limit).
        Find(&posts).Error
    
    return posts, err
}
```

## 提示 8：用户推荐

使用子查询查找兴趣相似的用户：

```go
func GetUserRecommendations(db *gorm.DB, userID uint, limit int) ([]User, error) {
    var users []User
    
    // 找到在与当前用户相同类别的帖子上点赞过的其他用户
    err := db.Where("id != ? AND id IN (?)", userID,
        db.Model(&Like{}).
            Select("DISTINCT likes.user_id").
            Joins("JOIN posts ON likes.post_id = posts.id").
            Joins("JOIN posts p2 ON p2.category = posts.category").
            Joins("JOIN likes l2 ON l2.post_id = p2.id").
            Where("l2.user_id = ?", userID)).
        Limit(limit).
        Find(&users).Error
    
    return users, err
}
```

## 查询模式

### 聚合查询
```go
// 带分组的计数
var results []struct {
    UserID    uint
    PostCount int64
}
db.Model(&Post{}).
   Select("user_id, COUNT(*) as post_count").
   Group("user_id").
   Order("post_count DESC").
   Scan(&results)
```

### 复杂连接
```go
// 连接多张表
var posts []Post
db.Joins("User").
   Joins("LEFT JOIN likes ON posts.id = likes.post_id").
   Where("posts.category = ?", category).
   Group("posts.id").
   Having("COUNT(likes.id) > ?", minLikes).
   Find(&posts)
```

### 子查询
```go
// 使用子查询进行筛选
var users []User
db.Where("id IN (?)", 
    db.Model(&Post{}).
       Select("user_id").
       Group("user_id").
       Having("COUNT(*) > ?", 5)).
   Find(&users)
```

### 分页
```go
func GetPaginatedResults(db *gorm.DB, page, pageSize int) ([]Post, int64, error) {
    var posts []Post
    var total int64
    
    // 获取总数
    db.Model(&Post{}).Count(&total)
    
    // 获取分页结果
    offset := (page - 1) * pageSize
    err := db.Offset(offset).Limit(pageSize).Find(&posts).Error
    
    return posts, total, err
}
```

## 性能优化

### 使用索引
```go
// 在模型中添加索引
type User struct {
    ID       uint   `gorm:"primaryKey"`
    Username string `gorm:"uniqueIndex"`
    Country  string `gorm:"index"`
}

type Post struct {
    ID        uint   `gorm:"primaryKey"`
    UserID    uint   `gorm:"index"`
    Category  string `gorm:"index"`
    CreatedAt time.Time `gorm:"index"`
}
```

### 避免 N+1 查询
```go
// 正确做法：使用预加载
var users []User
db.Preload("Posts").Find(&users)

// 错误做法：N+1 查询
var users []User
db.Find(&users)
for _, user := range users {
    db.Model(&user).Association("Posts").Find(&user.Posts)
}
```

### 限制结果集
```go
// 始终限制大数据集的结果
db.Limit(100).Find(&users)

// 对于大数据集使用基于游标的分页
db.Where("id > ?", cursor).Limit(50).Find(&posts)
```

## 错误处理

1. **检查每个数据库操作后的错误**
2. **处理空结果** - 返回空切片，而不是 nil
3. **验证输入参数** - 检查页码、限制值等是否有效
4. **处理数据库错误** - 如连接问题、约束冲突等

## 测试策略

### 设置测试数据
```go
func setupTestData(db *gorm.DB) {
    // 创建用户
    users := []User{
        {Username: "user1", Email: "user1@test.com", Age: 25, Country: "USA"},
        {Username: "user2", Email: "user2@test.com", Age: 30, Country: "Canada"},
    }
    for i := range users {
        db.Create(&users[i])
    }
    
    // 创建帖子
    posts := []Post{
        {Title: "Post 1", Content: "Content 1", UserID: users[0].ID, Category: "tech"},
        {Title: "Post 2", Content: "Content 2", UserID: users[0].ID, Category: "sports"},
    }
    for i := range posts {
        db.Create(&posts[i])
    }
    
    // 创建点赞
    likes := []Like{
        {UserID: users[1].ID, PostID: posts[0].ID},
        {UserID: users[0].ID, PostID: posts[1].ID},
    }
    for i := range likes {
        db.Create(&likes[i])
    }
}
```

### 测试聚合查询
```go
// 测试按发帖数量排序的顶级用户
users, err := GetTopUsersByPostCount(db, 3)
assert.NoError(t, err)
assert.Len(t, users, 2) // 只有 2 个用户有帖子
assert.Equal(t, "user1", users[0].Username) // user1 有 2 篇帖子
```

## 常见模式

### 时间过滤
```go
// 按时间段过滤
db.Where("created_at >= ?", time.Now().AddDate(0, 0, -days))
```

### 全文搜索
```go
// 简单的 LIKE 搜索
db.Where("title LIKE ? OR content LIKE ?", 
    "%"+query+"%", "%"+query+"%")
```

### 条件查询
```go
// 条件构建查询
query := db.Model(&Post{})
if category != "" {
    query = query.Where("category = ?", category)
}
if userID != 0 {
    query = query.Where("user_id = ?", userID)
}
query.Find(&posts)
```

## 调试技巧

1. **启用 GORM 日志**：
```go
db = db.Debug()
```

2. **检查查询结果**：
```go
// 打印查询结果
var count int64
db.Model(&User{}).Count(&count)
fmt.Printf("总用户数: %d\n", count)
```

3. **验证关联关系**：
```go
// 检查关联数据是否已加载
user := User{}
db.Preload("Posts").First(&user, userID)
fmt.Printf("用户有 %d 篇帖子\n", len(user.Posts))
```

## 应避免的常见错误

1. **未使用预加载** - 会导致 N+1 查询问题
2. **忘记限制结果** - 可能导致性能问题
3. **未处理空结果** - 返回空切片，而不是 nil
4. **未使用事务** - 对涉及多张表的复杂操作
5. **未优化查询** - 使用合适的索引和查询模式

## 有用的 GORM 方法

- `db.Joins()` - 连接表
- `db.Preload()` - 预加载相关数据
- `db.Group()` - 分组结果
- `db.Having()` - 过滤分组后的结果
- `db.Select()` - 选择特定字段或聚合
- `db.Count()` - 计算记录数
- `db.Offset()` / `db.Limit()` - 分页
- `db.Order()` - 排序结果
- `db.Scan()` - 将结果扫描到结构体

## SQLite 特定注意事项

- SQLite 不支持像 MySQL 那样的全文搜索
- 使用 `LIKE` 进行文本搜索
- 某些复杂的聚合操作可能较慢
- 注意大数据集的处理

## 最后建议

1. **从简单查询开始** - 先让基本功能正常运行
2. **用小数据集测试** - 在扩大规模前验证逻辑
3. **利用学习资源** - 查阅 GORM 文档获取示例
4. **分析查询性能** - 使用 GORM 调试模式查看实际 SQL
5. **考虑缓存** - 对频繁访问的数据进行缓存

## 性能检查清单

- [ ] 使用适当的索引
- [ ] 限制结果集大小
- [ ] 使用预加载避免 N+1 查询
- [ ] 对复杂操作使用事务
- [ ] 优化聚合查询
- [ ] 处理边界情况和错误
- [ ] 使用真实数据量进行测试