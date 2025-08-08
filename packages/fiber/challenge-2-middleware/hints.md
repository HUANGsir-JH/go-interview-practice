# 挑战 2 提示：中间件与请求/响应处理

## 提示 1：设置 Fiber 应用

从一个干净的 Fiber 应用开始：

```go
app := fiber.New(fiber.Config{
    ErrorHandler: func(c *fiber.Ctx, err error) error {
        // 自定义错误处理器
        return c.Status(500).JSON(fiber.Map{
            "success": false,
            "error": "内部服务器错误",
        })
    },
})
```

## 提示 2：中间件顺序

按正确顺序应用中间件：

```go
app.Use(ErrorHandlerMiddleware())
app.Use(RequestIDMiddleware())
app.Use(LoggingMiddleware())
app.Use(CORSMiddleware())
app.Use(RateLimitMiddleware())
```

## 提示 3：请求 ID 生成

使用 UUID 生成唯一的请求 ID：

```go
func RequestIDMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        requestID := uuid.New().String()
        c.Locals("request_id", requestID)
        c.Set("X-Request-ID", requestID)
        return c.Next()
    }
}
```

## 提示 4：自定义日志记录

记录请求并包含耗时信息：

```go
func LoggingMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        start := time.Now()
        requestID := c.Locals("request_id").(string)
        
        err := c.Next()
        
        duration := time.Since(start)
        fmt.Printf("[%s] %s %s %d %v %s\n",
            requestID,
            c.Method(),
            c.Path(),
            c.Response().StatusCode(),
            duration,
            c.IP(),
        )
        
        return err
    }
}
```

## 提示 5：限流

实现简单的内存限流：

```go
var rateLimitMap = make(map[string][]time.Time)
var rateLimitMutex sync.RWMutex

func RateLimitMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        ip := c.IP()
        now := time.Now()
        
        rateLimitMutex.Lock()
        defer rateLimitMutex.Unlock()
        
        // 清理旧条目
        if times, exists := rateLimitMap[ip]; exists {
            var validTimes []time.Time
            for _, t := range times {
                if now.Sub(t) < time.Minute {
                    validTimes = append(validTimes, t)
                }
            }
            rateLimitMap[ip] = validTimes
        }
        
        // 检查限制
        if len(rateLimitMap[ip]) >= 100 {
            return c.Status(429).JSON(fiber.Map{
                "success": false,
                "error": "请求频率超出限制",
            })
        }
        
        // 添加当前请求
        rateLimitMap[ip] = append(rateLimitMap[ip], now)
        
        return c.Next()
    }
}
```

## 提示 6：路由分组

使用分组组织路由：

```go
// 公共路由
public := app.Group("/")
public.Get("/ping", pingHandler)
public.Get("/articles", getArticlesHandler)
public.Get("/articles/:id", getArticleHandler)

// 受保护的路由
protected := app.Group("/", AuthMiddleware())
protected.Post("/articles", createArticleHandler)
protected.Put("/articles/:id", updateArticleHandler)
protected.Delete("/articles/:id", deleteArticleHandler)
protected.Get("/admin/stats", getStatsHandler)
```