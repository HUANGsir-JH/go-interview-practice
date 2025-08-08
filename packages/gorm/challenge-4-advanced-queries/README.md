# 挑战 4：高级查询

使用 GORM 构建一个 **社交媒体分析系统**，展示高级查询技术、聚合操作和复杂数据分析。

## 挑战要求

创建一个 Go 应用程序，实现以下功能：

1. **复杂查询** - 高级过滤、排序和分页
2. **聚合操作** - 分组、计数、求和、平均值运算
3. **子查询** - 嵌套查询和相关子查询
4. **原生 SQL** - 必要时使用自定义 SQL 查询
5. **查询优化** - 高效的数据检索模式

## 数据模型

```go
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Username  string    `gorm:"unique;not null"`
    Email     string    `gorm:"unique;not null"`
    Age       int       `gorm:"not null"`
    Country   string    `gorm:"not null"`
    CreatedAt time.Time
    Posts     []Post    `gorm:"foreignKey:UserID"`
    Likes     []Like    `gorm:"foreignKey:UserID"`
}

type Post struct {
    ID          uint      `gorm:"primaryKey"`
    Title       string    `gorm:"not null"`
    Content     string    `gorm:"type:text"`
    UserID      uint      `gorm:"not null"`
    User        User      `gorm:"foreignKey:UserID"`
    Category    string    `gorm:"not null"`
    ViewCount   int       `gorm:"default:0"`
    IsPublished bool      `gorm:"default:true"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
    Likes       []Like    `gorm:"foreignKey:PostID"`
}

type Like struct {
    ID        uint      `gorm:"primaryKey"`
    UserID    uint      `gorm:"not null"`
    PostID    uint      `gorm:"not null"`
    User      User      `gorm:"foreignKey:UserID"`
    Post      Post      `gorm:"foreignKey:PostID"`
    CreatedAt time.Time
}
```

## 必需函数

实现以下函数：
- `ConnectDB() (*gorm.DB, error)` - 数据库连接并自动迁移
- `GetTopUsersByPostCount(db *gorm.DB, limit int) ([]User, error)` - 获取发帖数量最多的用户
- `GetPostsByCategoryWithUserInfo(db *gorm.DB, category string, page, pageSize int) ([]Post, int64, error)` - 获取指定分类的帖子并分页，包含用户信息
- `GetUserEngagementStats(db *gorm.DB, userID uint) (map[string]interface{}, error)` - 获取用户的互动统计数据
- `GetPopularPostsByLikes(db *gorm.DB, days int, limit int) ([]Post, error)` - 获取指定时间段内点赞数最多的热门帖子
- `GetCountryUserStats(db *gorm.DB) ([]map[string]interface{}, error)` - 按国家统计用户数据
- `SearchPostsByContent(db *gorm.DB, query string, limit int) ([]Post, error)` - 根据内容搜索帖子
- `GetUserRecommendations(db *gorm.DB, userID uint, limit int) ([]User, error)` - 根据相似兴趣推荐用户

## 查询示例

**按发帖数量排名的顶级用户：**
```sql
SELECT users.*, COUNT(posts.id) as post_count 
FROM users 
LEFT JOIN posts ON users.id = posts.user_id 
GROUP BY users.id 
ORDER BY post_count DESC 
LIMIT 10
```

**按点赞数排名的热门帖子：**
```sql
SELECT posts.*, COUNT(likes.id) as like_count 
FROM posts 
LEFT JOIN likes ON posts.id = likes.post_id 
WHERE posts.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY posts.id 
ORDER BY like_count DESC 
LIMIT 20
```

## 测试要求

你的解决方案必须通过以下测试：
- 正确聚合计算按发帖数量排名的顶级用户
- 带用户信息的分页帖子获取
- 用户互动统计数据的正确计算
- 按时间段和点赞数筛选热门帖子
- 按国家划分的用户统计数据
- 全文搜索功能
- 用户推荐算法
- 查询性能与优化