# 学习：高级 Fiber 中间件模式

## 🌟 **什么是中间件？**

中间件函数在请求-响应周期中执行，可以：
- 在路由处理器之前执行代码
- 修改请求或响应对象
- 结束请求-响应周期
- 调用下一个中间件函数

### **Fiber 中的中间件**
Fiber 中间件使用与 Express.js 类似的模式，通过 `c.Next()` 函数：

```go
func MyMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        // 处理前逻辑
        
        err := c.Next() // 执行下一个中间件/处理器
        
        // 处理后逻辑
        
        return err
    }
}
```

## 🔄 **中间件执行顺序**

中间件按注册顺序执行：

```
请求 → MW1 → MW2 → MW3 → 处理器 → MW3 → MW2 → MW1 → 响应
```

### **最佳实践顺序**
1. **错误恢复** - 首先捕获 panic
2. **请求 ID** - 跟踪请求
3. **日志记录** - 使用请求 ID 记录日志
4. **CORS** - 处理跨域请求
5. **限流** - 防止滥用
6. **认证** - 验证用户
7. **路由处理器** - 业务逻辑

## 🛠️ **必备中间件模式**

### **1. 请求 ID 中间件**
在整个应用中跟踪请求：

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

### **2. 日志中间件**
监控请求性能：

```go
func LoggingMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        start := time.Now()
        
        err := c.Next()
        
        duration := time.Since(start)
        log.Printf("%s %s %d %v",
            c.Method(),
            c.Path(),
            c.Response().StatusCode(),
            duration,
        )
        
        return err
    }
}
```

### **3. CORS 中间件**
启用跨域请求：

```go
func CORSMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        c.Set("Access-Control-Allow-Origin", "*")
        c.Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        c.Set("Access-Control-Allow-Headers", "Content-Type,Authorization")
        
        if c.Method() == "OPTIONS" {
            return c.SendStatus(204)
        }
        
        return c.Next()
    }
}
```

### **4. 认证中间件**
使用 API 密钥或令牌保护路由：

```go
func AuthMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        apiKey := c.Get("X-API-Key")
        
        if !isValidAPIKey(apiKey) {
            return c.Status(401).JSON(fiber.Map{
                "error": "未授权",
            })
        }
        
        c.Locals("api_key", apiKey)
        return c.Next()
    }
}
```

## 📊 **限流策略**

### **固定窗口**
简单但可能允许突发流量：

```go
func FixedWindowRateLimit() fiber.Handler {
    requests := make(map[string]int)
    lastReset := time.Now()
    
    return func(c *fiber.Ctx) error {
        now := time.Now()
        ip := c.IP()
        
        // 每分钟重置窗口
        if now.Sub(lastReset) >= time.Minute {
            requests = make(map[string]int)
            lastReset = now
        }
        
        requests[ip]++
        if requests[ip] > 100 {
            return c.Status(429).JSON(fiber.Map{
                "error": "超出速率限制",
            })
        }
        
        return c.Next()
    }
}
```

### **滑动窗口**
更精确但占用更多内存：

```go
func SlidingWindowRateLimit() fiber.Handler {
    requests := make(map[string][]time.Time)
    
    return func(c *fiber.Ctx) error {
        now := time.Now()
        ip := c.IP()
        
        // 清理旧请求
        var validRequests []time.Time
        for _, reqTime := range requests[ip] {
            if now.Sub(reqTime) < time.Minute {
                validRequests = append(validRequests, reqTime)
            }
        }
        
        if len(validRequests) >= 100 {
            return c.Status(429).JSON(fiber.Map{
                "error": "超出速率限制",
            })
        }
        
        requests[ip] = append(validRequests, now)
        return c.Next()
    }
}
```

## 🔒 **错误处理模式**

### **集中式错误处理器**
在一个地方处理所有错误：

```go
func ErrorHandlerMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("恢复 panic: %v", r)
                c.Status(500).JSON(fiber.Map{
                    "success": false,
                    "error": "内部服务器错误",
                })
            }
        }()
        
        return c.Next()
    }
}
```

### **自定义错误类型**
创建特定的错误类型：

```go
type APIError struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

func (e APIError) Error() string {
    return e.Message
}

func ValidationError(message string) APIError {
    return APIError{
        Code:    400,
        Message: message,
    }
}
```

## 🎯 **上下文与状态管理**

### **在上下文中存储数据**
在中间件之间共享数据：

```go
// 存储数据
c.Locals("user_id", 123)
c.Locals("request_start", time.Now())

// 获取数据
userID := c.Locals("user_id").(int)
startTime := c.Locals("request_start").(time.Time)
```

### **请求作用域数据**
将数据与特定请求关联：

```go
type RequestContext struct {
    UserID    int
    RequestID string
    StartTime time.Time
}

func ContextMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        ctx := &RequestContext{
            RequestID: uuid.New().String(),
            StartTime: time.Now(),
        }
        
        c.Locals("ctx", ctx)
        return c.Next()
    }
}
```

## 📈 **性能考虑**

### **高效中间件**
- 避免在中间件中进行耗时计算
- 对外部服务使用连接池
- 缓存频繁访问的数据
- 正确清理资源

### **内存管理**
```go
func EfficientMiddleware() fiber.Handler {
    // 在处理器外部初始化
    cache := make(map[string]interface{})
    
    return func(c *fiber.Ctx) error {
        // 仅执行轻量级操作
        key := c.Get("Cache-Key")
        if data, exists := cache[key]; exists {
            c.Locals("cached_data", data)
        }
        
        return c.Next()
    }
}
```

## 🔧 **测试中间件**

### **单元测试**
隔离测试中间件：

```go
func TestRequestIDMiddleware(t *testing.T) {
    app := fiber.New()
    app.Use(RequestIDMiddleware())
    app.Get("/test", func(c *fiber.Ctx) error {
        return c.SendString("OK")
    })
    
    req := httptest.NewRequest("GET", "/test", nil)
    resp, _ := app.Test(req)
    
    assert.NotEmpty(t, resp.Header.Get("X-Request-ID"))
}
```

### **集成测试**
测试中间件链：

```go
func TestMiddlewareChain(t *testing.T) {
    app := fiber.New()
    app.Use(RequestIDMiddleware())
    app.Use(LoggingMiddleware())
    app.Use(AuthMiddleware())
    
    // 使用有效认证测试
    req := httptest.NewRequest("GET", "/protected", nil)
    req.Header.Set("X-API-Key", "valid-key")
    
    resp, _ := app.Test(req)
    assert.Equal(t, 200, resp.StatusCode)
}
```

## 🎯 **最佳实践**

1. **保持中间件专注** - 每个中间件只负责一个职责
2. **顺序很重要** - 将中间件按逻辑顺序排列
3. **优雅处理错误** - 不要让中间件导致应用崩溃
4. **使用上下文共享** - 将请求作用域数据存储在上下文中
5. **充分测试** - 单元测试每个中间件
6. **监控性能** - 跟踪中间件执行时间
7. **清理资源** - 在 defer 语句中释放资源

## 📚 **下一步**

掌握中间件模式后：
1. **验证与错误处理** - 输入验证和错误响应
2. **认证与授权** - JWT 令牌和基于角色的访问控制
3. **数据库集成** - 连接数据库
4. **测试策略** - 全面的测试方法