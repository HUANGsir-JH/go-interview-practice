# 学习 GORM 高级查询

## 概述

GORM 中的高级查询允许您执行复杂的数据库操作、聚合和分析。本挑战聚焦于掌握高级查询技术，以构建高效且强大的数据检索系统。

## 查询构建

### 1. 方法链式调用
GORM 允许您链式调用查询方法以实现复杂查询：

```go
var users []User
db.Where("age > ?", 18).
   Where("country = ?", "USA").
   Order("created_at DESC").
   Limit(10).
   Find(&users)
```

### 2. 带条件的预加载
使用特定条件预加载相关数据：

```go
var users []User
db.Preload("Posts", "is_published = ?", true).
   Preload("Posts.Tags").
   Find(&users)
```

## 聚合

### 1. 计数
按条件统计记录数量：

```go
var count int64
db.Model(&User{}).Where("country = ?", "USA").Count(&count)

// 去重计数
db.Model(&User{}).Distinct("country").Count(&count)
```

### 2. 求和、平均值、最小值、最大值
执行数学聚合操作：

```go
var total float64
db.Model(&Product{}).Select("SUM(price)").Scan(&total)

var avgPrice float64
db.Model(&Product{}).Select("AVG(price)").Scan(&avgPrice)

var maxPrice float64
db.Model(&Product{}).Select("MAX(price)").Scan(&maxPrice)
```

### 3. 分组
按特定字段分组结果：

```go
type CountryStats struct {
    Country string
    Count   int64
    AvgAge  float64
}

var stats []CountryStats
db.Model(&User{}).
   Select("country, COUNT(*) as count, AVG(age) as avg_age").
   Group("country").
   Scan(&stats)
```

## 复杂查询

### 1. 子查询
使用子查询进行复杂过滤：

```go
// 查找拥有超过 5 篇文章的用户
var users []User
db.Where("id IN (?)", 
    db.Model(&Post{}).
       Select("user_id").
       Group("user_id").
       Having("COUNT(*) > ?", 5)).
   Find(&users)
```

### 2. 连接查询
执行复杂的连接操作：

```go
var results []struct {
    UserName  string
    PostCount int64
    LikeCount int64
}

db.Table("users").
   Select("users.username, COUNT(DISTINCT posts.id) as post_count, COUNT(likes.id) as like_count").
   Joins("LEFT JOIN posts ON users.id = posts.user_id").
   Joins("LEFT JOIN likes ON posts.id = likes.post_id").
   Group("users.id, users.username").
   Scan(&results)
```

### 3. 原生 SQL
使用原生 SQL 实现复杂查询：

```go
var users []User
db.Raw(`
    SELECT u.*, COUNT(p.id) as post_count 
    FROM users u 
    LEFT JOIN posts p ON u.id = p.user_id 
    WHERE u.country = ? 
    GROUP BY u.id 
    HAVING post_count > ? 
    ORDER BY post_count DESC
`, "USA", 5).Scan(&users)
```

## 分页

### 1. 偏移与限制
实现分页功能：

```go
func GetPaginatedPosts(db *gorm.DB, page, pageSize int) ([]Post, int64, error) {
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

### 2. 游标分页
对于大数据集有更好的性能表现：

```go
func GetPostsByCursor(db *gorm.DB, cursor uint, limit int) ([]Post, error) {
    var posts []Post
    err := db.Where("id > ?", cursor).
              Order("id ASC").
              Limit(limit).
              Find(&posts).Error
    return posts, err
}
```

## 全文搜索

### 1. LIKE 查询
简单的文本搜索：

```go
var posts []Post
db.Where("title LIKE ? OR content LIKE ?", 
    "%"+query+"%", "%"+query+"%").Find(&posts)
```

### 2. 全文搜索（MySQL）
实现更高级的搜索功能：

```go
var posts []Post
db.Where("MATCH(title, content) AGAINST(? IN BOOLEAN MODE)", query).Find(&posts)
```

## 查询优化

### 1. 选择特定字段
仅选择需要的字段：

```go
var users []User
db.Select("id, username, email").Find(&users)
```

### 2. 使用索引
确保对频繁查询的字段建立适当的索引：

```go
// 在模型中添加索引
type User struct {
    ID       uint   `gorm:"primaryKey"`
    Username string `gorm:"uniqueIndex"`
    Email    string `gorm:"uniqueIndex"`
    Country  string `gorm:"index"`
}
```

### 3. 避免 N+1 查询
使用预加载避免多次查询：

```go
// 正确：单次查询并预加载
var users []User
db.Preload("Posts").Find(&users)

// 错误：N+1 查询
var users []User
db.Find(&users)
for _, user := range users {
    db.Model(&user).Association("Posts").Find(&user.Posts)
}
```

## 分析查询

### 1. 时间维度分析
按时间段分析数据：

```go
type DailyStats struct {
    Date  string
    Count int64
}

var stats []DailyStats
db.Model(&Post{}).
   Select("DATE(created_at) as date, COUNT(*) as count").
   Where("created_at >= ?", time.Now().AddDate(0, 0, -30)).
   Group("DATE(created_at)").
   Order("date ASC").
   Scan(&stats)
```

### 2. 用户参与度指标
计算用户参与度：

```go
func GetUserEngagement(db *gorm.DB, userID uint) map[string]interface{} {
    var stats map[string]interface{}
    
    // 获取文章数量
    var postCount int64
    db.Model(&Post{}).Where("user_id = ?", userID).Count(&postCount)
    
    // 获取收到的总点赞数
    var likesReceived int64
    db.Model(&Like{}).
       Joins("JOIN posts ON likes.post_id = posts.id").
       Where("posts.user_id = ?", userID).
       Count(&likesReceived)
    
    // 获取每篇文章的平均浏览量
    var avgViews float64
    db.Model(&Post{}).
       Select("AVG(view_count)").
       Where("user_id = ?", userID).
       Scan(&avgViews)
    
    stats = map[string]interface{}{
        "total_posts":           postCount,
        "total_likes_received":  likesReceived,
        "average_views_per_post": avgViews,
    }
    
    return stats
}
```

## 高级模式

### 1. 查询作用域
创建可复用的查询条件：

```go
func (db *gorm.DB) ActiveUsers() *gorm.DB {
    return db.Where("is_active = ?", true)
}

func (db *gorm.DB) PublishedPosts() *gorm.DB {
    return db.Where("is_published = ?", true)
}

// 使用示例
var users []User
db.ActiveUsers().Find(&users)

var posts []Post
db.PublishedPosts().Preload("User").Find(&posts)
```

### 2. 查询钩子
为查询添加自定义逻辑：

```go
func (u *User) AfterFind(tx *gorm.DB) error {
    // 查询后计算额外字段
    u.FullName = u.FirstName + " " + u.LastName
    return nil
}
```

### 3. 自定义扫描器
处理复杂的查询结果：

```go
type UserStats struct {
    UserID    uint
    Username  string
    PostCount int64
    LikeCount int64
}

func (us *UserStats) Scan(value interface{}) error {
    // 自定义扫描逻辑
    return nil
}
```

## 性能提示

### 1. 使用索引
为频繁查询的字段创建索引：

```sql
CREATE INDEX idx_users_country ON users(country);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_likes_post_id ON likes(post_id);
```

### 2. 限制结果集
始终限制大型结果集：

```go
db.Limit(100).Find(&users) // 限制返回 100 条结果
```

### 3. 高效使用计数
在分页时高效使用计数：

```go
// 正确：使用计数获取总数
var total int64
db.Model(&User{}).Count(&total)

// 错误：加载所有记录后再计数
var users []User
db.Find(&users)
total := len(users)
```

### 4. 缓存结果
缓存频繁访问的数据：

```go
func GetCachedUserStats(userID uint) map[string]interface{} {
    cacheKey := fmt.Sprintf("user_stats_%d", userID)
    
    // 先检查缓存
    if cached, found := cache.Get(cacheKey); found {
        return cached.(map[string]interface{})
    }
    
    // 计算统计数据
    stats := calculateUserStats(userID)
    
    // 缓存 5 分钟
    cache.Set(cacheKey, stats, 5*time.Minute)
    
    return stats
}
```

## 资源

- [GORM 高级查询](https://gorm.io/docs/advanced_query.html)
- [GORM 原生 SQL](https://gorm.io/docs/raw_sql.html)
- [GORM 作用域](https://gorm.io/docs/scopes.html)
- [GORM 钩子](https://gorm.io/docs/hooks.html)
- [SQL 性能调优](https://use-the-index-luke.com/)

## 练习题

1. 构建一个社交媒体分析仪表盘  
2. 实现带筛选功能的搜索引擎  
3. 创建一个推荐系统  
4. 构建一个包含聚合功能的报表系统  
5. 实现实时分析查询  

这些练习将帮助您掌握高级查询技术，并构建高效的查询系统。