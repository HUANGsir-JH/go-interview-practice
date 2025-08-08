# 学习：Gin 中间件高级模式

## 🌟 **什么是中间件？**

Gin 中的中间件是在路由处理器**之前和之后**运行的代码。可以将其视为一系列函数链，能够：
- **拦截**请求在到达处理器之前
- **修改**请求和响应
- **添加**日志记录、认证、CORS 等功能
- **全局处理**错误和恐慌

### **中间件链**
```
请求 → 中间件1 → 中间件2 → 处理器 → 中间件2 → 中间件1 → 响应
```

## 🔗 **中间件执行流程**

### **基本中间件结构**
```go
func MyMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 之前：此处代码在请求处理前运行
        fmt.Println("请求前")
        
        c.Next() // 调用下一个中间件/处理器
        
        // 之后：此处代码在请求处理后运行  
        fmt.Println("请求后")
    }
}
```

### **中间件注册**
```go
router := gin.Default()

// 全局中间件（对所有路由生效）
router.Use(MyMiddleware())

// 组中间件（对特定路由组生效）
api := router.Group("/api")
api.Use(AuthMiddleware())
{
    api.GET("/users", getUsers)
}

// 路由特有中间件
router.GET("/admin", AdminMiddleware(), adminHandler)
```

## 🔐 **认证中间件**

### **API 密钥认证**
```go
func APIKeyAuth() gin.HandlerFunc {
    return func(c *gin.Context) {
        apiKey := c.GetHeader("X-API-Key")
        
        if apiKey == "" {
            c.JSON(401, gin.H{"error": "需要 API 密钥"})
            c.Abort() // 停止中间件链
            return
        }
        
        // 验证 API 密钥
        if !isValidAPIKey(apiKey) {
            c.JSON(401, gin.H{"error": "无效的 API 密钥"})
            c.Abort()
            return
        }
        
        // 将用户信息存入上下文
        c.Set("user_id", getUserIDFromAPIKey(apiKey))
        c.Set("user_role", getUserRole(apiKey))
        
        c.Next() // 继续下一个中间件/处理器
    }
}
```

### **基于角色的访问控制**
```go
func RequireRole(requiredRole string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole := c.GetString("user_role")
        
        if userRole != requiredRole {
            c.JSON(403, gin.H{"error": "权限不足"})
            c.Abort()
            return
        }
        
        c.Next()
    }
}

// 使用示例：要求管理员角色
router.DELETE("/users/:id", RequireRole("admin"), deleteUser)
```

## 📝 **日志中间件**

### **自定义请求日志**
```go
func CustomLogger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        
        c.Next()
        
        // 计算请求耗时
        duration := time.Since(start)
        
        // 记录请求详情
        log.Printf("[%s] %s %s %d %v %s",
            c.GetString("request_id"),
            c.Request.Method,
            path,
            c.Writer.Status(),
            duration,
            c.ClientIP(),
        )
    }
}
```

### **带上下文的结构化日志**
```go
func StructuredLogger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        duration := time.Since(start)
        
        entry := map[string]interface{}{
            "request_id": c.GetString("request_id"),
            "method":     c.Request.Method,
            "path":       c.Request.URL.Path,
            "status":     c.Writer.Status(),
            "duration":   duration.Milliseconds(),
            "ip":         c.ClientIP(),
            "user_agent": c.Request.UserAgent(),
        }
        
        if c.Writer.Status() >= 400 {
            log.Printf("ERROR: %+v", entry)
        } else {
            log.Printf("INFO: %+v", entry)
        }
    }
}
```

## 🌐 **CORS 中间件**

### **理解 CORS**
跨域资源共享（CORS）允许一个域名的网页访问另一个域名的资源。

### **自定义 CORS 实现**
```go
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        origin := c.Request.Header.Get("Origin")
        
        // 定义允许的来源
        allowedOrigins := map[string]bool{
            "http://localhost:3000":  true,
            "https://myapp.com":      true,
        }
        
        if allowedOrigins[origin] {
            c.Header("Access-Control-Allow-Origin", origin)
        }
        
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, X-Request-ID")
        c.Header("Access-Control-Allow-Credentials", "true")
        
        // 处理预检请求
        if c.Request.Method == "OPTIONS" {
            c.Status(204)
            c.Abort()
            return
        }
        
        c.Next()
    }
}
```

## ⏱️ **限流中间件**

### **简单的内存限流器**
```go
type RateLimiter struct {
    visitors map[string]*visitor
    mu       sync.RWMutex
}

type visitor struct {
    limiter  *rate.Limiter
    lastSeen time.Time
}

func NewRateLimiter(requests int, duration time.Duration) *RateLimiter {
    rl := &RateLimiter{
        visitors: make(map[string]*visitor),
    }
    
    // 每分钟清理旧访客
    go rl.cleanupVisitors()
    
    return rl
}

func (rl *RateLimiter) getVisitor(ip string) *rate.Limiter {
    rl.mu.Lock()
    defer rl.mu.Unlock()
    
    v, exists := rl.visitors[ip]
    if !exists {
        limiter := rate.NewLimiter(rate.Every(time.Minute), 100) // 每分钟 100 次请求
        rl.visitors[ip] = &visitor{limiter, time.Now()}
        return limiter
    }
    
    v.lastSeen = time.Now()
    return v.limiter
}

func (rl *RateLimiter) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        limiter := rl.getVisitor(c.ClientIP())
        
        if !limiter.Allow() {
            c.Header("X-RateLimit-Limit", "100")
            c.Header("X-RateLimit-Remaining", "0")
            c.JSON(429, gin.H{"error": "超出速率限制"})
            c.Abort()
            return
        }
        
        c.Next()
    }
}
```

## 🆔 **请求 ID 中间件**

### **UUID 生成**
```go
import "github.com/google/uuid"

func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查请求 ID 是否已在头部存在
        requestID := c.GetHeader("X-Request-ID")
        
        if requestID == "" {
            // 生成新的 UUID
            requestID = uuid.New().String()
        }
        
        // 将其存入上下文供其他中间件/处理器使用
        c.Set("request_id", requestID)
        
        // 添加到响应头
        c.Header("X-Request-ID", requestID)
        
        c.Next()
    }
}
```

## ❌ **错误处理中间件**

### **集中式错误处理器**
```go
type APIError struct {
    StatusCode int    `json:"-"`
    Code       string `json:"code"`
    Message    string `json:"message"`
    Details    string `json:"details,omitempty"`
}

func (e APIError) Error() string {
    return e.Message
}

func ErrorHandler() gin.HandlerFunc {
    return gin.CustomRecovery(func(c *gin.Context, recovered interface{}) {
        var apiErr APIError
        
        switch err := recovered.(type) {
        case APIError:
            apiErr = err
        case error:
            apiErr = APIError{
                StatusCode: 500,
                Code:       "INTERNAL_ERROR",
                Message:    "内部服务器错误",
                Details:    err.Error(),
            }
        default:
            apiErr = APIError{
                StatusCode: 500,
                Code:       "PANIC",
                Message:    "内部服务器错误",
                Details:    fmt.Sprintf("%v", recovered),
            }
        }
        
        c.JSON(apiErr.StatusCode, gin.H{
            "success":    false,
            "error":      apiErr.Message,
            "code":       apiErr.Code,
            "request_id": c.GetString("request_id"),
        })
    })
}
```

## 🔍 **内容类型验证**

### **JSON 内容类型中间件**
```go
func RequireJSON() gin.HandlerFunc {
    return func(c *gin.Context) {
        if c.Request.Method == "POST" || c.Request.Method == "PUT" {
            contentType := c.GetHeader("Content-Type")
            
            if !strings.HasPrefix(contentType, "application/json") {
                c.JSON(415, gin.H{
                    "error":   "Content-Type 必须为 application/json",
                    "code":    "INVALID_CONTENT_TYPE",
                })
                c.Abort()
                return
            }
        }
        
        c.Next()
    }
}
```

## 🔄 **上下文数据共享**

### **在中间件之间传递数据**
```go
// 在中间件中设置数据
func SetUserMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 认证用户...
        user := User{ID: 123, Name: "John Doe"}
        
        c.Set("current_user", user)
        c.Set("user_id", user.ID)
        
        c.Next()
    }
}

// 在处理器中获取数据
func getUserHandler(c *gin.Context) {
    user, exists := c.Get("current_user")
    if !exists {
        c.JSON(401, gin.H{"error": "未找到用户"})
        return
    }
    
    currentUser := user.(User)
    c.JSON(200, currentUser)
}
```

## 🏗️ **中间件最佳实践**

### **1. 执行顺序很重要**
```go
router.Use(
    ErrorHandler(),      // 首先：捕获恐慌
    RequestIDMiddleware(), // 早期：生成请求 ID
    CORSMiddleware(),     // 早期：处理 CORS
    CustomLogger(),       // 记录请求
    RateLimiter(),        // 限流
    AuthMiddleware(),     // 认证（如需）
)
```

### **2. 优雅的错误处理**
```go
func SafeMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("中间件恐慌: %v", r)
                c.JSON(500, gin.H{"error": "内部服务器错误"})
                c.Abort()
            }
        }()
        
        c.Next()
    }
}
```

### **3. 性能考虑**
```go
// 缓存昂贵操作
var onceCache sync.Once
var expensiveData string

func OptimizedMiddleware() gin.HandlerFunc {
    onceCache.Do(func() {
        expensiveData = loadExpensiveData()
    })
    
    return func(c *gin.Context) {
        // 使用缓存数据
        c.Set("data", expensiveData)
        c.Next()
    }
}
```

## 🔗 **第三方中间件**

### **流行的 Gin 中间件**
```go
import (
    "github.com/gin-contrib/cors"
    "github.com/gin-contrib/sessions"
    "github.com/gin-contrib/gzip"
)

// CORS
router.Use(cors.Default())

// 会话
store := sessions.NewCookieStore([]byte("secret"))
router.Use(sessions.Sessions("mysession", store))

// Gzip 压缩
router.Use(gzip.Gzip(gzip.DefaultCompression))
```

## 🧪 **测试中间件**

### **单元测试中间件**
```go
func TestAuthMiddleware(t *testing.T) {
    gin.SetMode(gin.TestMode)
    
    router := gin.New()
    router.Use(APIKeyAuth())
    router.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "success"})
    })
    
    // 测试无 API 密钥的情况
    w := httptest.NewRecorder()
    req, _ := http.NewRequest("GET", "/test", nil)
    router.ServeHTTP(w, req)
    
    assert.Equal(t, 401, w.Code)
    
    // 测试有效 API 密钥
    w = httptest.NewRecorder()
    req, _ = http.NewRequest("GET", "/test", nil)
    req.Header.Set("X-API-Key", "valid-key")
    router.ServeHTTP(w, req)
    
    assert.Equal(t, 200, w.Code)
}
```

## 🌍 **实际应用场景**

### **生产环境中间件栈**
```go
func SetupMiddleware(router *gin.Engine) {
    // 安全
    router.Use(SecurityHeaders())
    router.Use(RateLimiter(100, time.Minute))
    
    // 可观测性
    router.Use(RequestID())
    router.Use(StructuredLogger())
    router.Use(Metrics())
    
    // CORS 与内容
    router.Use(CORS())
    router.Use(gzip.Gzip(gzip.DefaultCompression))
    
    // 错误处理
    router.Use(ErrorHandler())
    
    // 认证（用于受保护的路由）
    api := router.Group("/api/v1")
    api.Use(JWTAuth())
}
```

## 📚 **下一步**

掌握中间件后，可进一步探索：
1. **自定义校验器**：JSON Schema 校验中间件
2. **缓存**：响应缓存中间件
3. **熔断器**：容错模式
4. **分布式追踪**：OpenTelemetry 集成
5. **健康检查**：端点监控中间件