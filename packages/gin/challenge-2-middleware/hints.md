# 挑战 2 提示：中间件与请求/响应处理

## 提示 1：理解中间件

中间件函数在路由处理器之前运行。它们遵循以下模式：

```go
func MyMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 在此处编写预处理逻辑
        
        c.Next() // 重要：调用此方法以继续执行链
        
        // 在此处编写后处理逻辑（在处理器之后运行）
    }
}
```

## 提示 2：请求 ID 中间件

创建一个为每个请求添加唯一请求 ID 的中间件：

```go
import "github.com/google/uuid"

func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := uuid.New().String()
        c.Set("request_id", requestID)
        c.Header("X-Request-ID", requestID)
        c.Next()
    }
}
```

## 提示 3：日志中间件结构

构建一个跟踪请求详情的日志中间件：

```go
func LoggingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        duration := time.Since(start)
        log.Printf("[%s] %s %s - %v", 
            c.Request.Method, 
            c.Request.URL.Path, 
            c.ClientIP(), 
            duration)
    }
}
```

## 提示 4：CORS 中间件实现

处理跨域资源共享以支持网页客户端访问：

```go
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Request-ID")
        
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }
        
        c.Next()
    }
}
```

## 提示 5：使用内存存储的限流

使用内存存储实现基本的请求频率限制：

```go
import "golang.org/x/time/rate"

var rateLimiters = make(map[string]*rate.Limiter)
var mu sync.Mutex

func RateLimitMiddleware(requestsPerSecond int) gin.HandlerFunc {
    return func(c *gin.Context) {
        clientIP := c.ClientIP()
        
        mu.Lock()
        limiter, exists := rateLimiters[clientIP]
        if !exists {
            limiter = rate.NewLimiter(rate.Limit(requestsPerSecond), requestsPerSecond*2)
            rateLimiters[clientIP] = limiter
        }
        mu.Unlock()
        
        if !limiter.Allow() {
            c.JSON(429, gin.H{"error": "请求频率超出限制"})
            c.Abort()
            return
        }
        
        c.Next()
    }
}
```

## 提示 6：设置带中间件的路由器

按正确顺序将中间件应用到你的路由器：

```go
func setupRouter() *gin.Engine {
    router := gin.New() // 从干净的路由器开始
    
    // 按顺序添加中间件
    router.Use(LoggingMiddleware())
    router.Use(RequestIDMiddleware())
    router.Use(CORSMiddleware())
    router.Use(RateLimitMiddleware(100)) // 每秒 100 次请求
    
    // 添加你的路由
    router.GET("/users", getUsers)
    router.POST("/users", createUser)
    
    return router
}
```