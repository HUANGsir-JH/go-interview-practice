# HTTP 认证中间件学习资料

## Go 中的 HTTP 服务器与中间件

Go 通过其标准库提供了构建 HTTP 服务器的优秀支持。本挑战聚焦于实现用于认证的 HTTP 中间件。

### Go 中的 HTTP 基础知识

Go 的 `net/http` 包提供了构建 HTTP 服务器所需的一切功能：

```go
package main

import (
    "fmt"
    "net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "你好，世界！")
}

func main() {
    http.HandleFunc("/hello", helloHandler)
    http.ListenAndServe(":8080", nil)
}
```

### 理解中间件

中间件函数位于客户端请求和应用程序逻辑之间。它们可以：

1. 处理传入的请求
2. 修改请求对象
3. 提前终止请求
4. 修改响应对象
5. 将多个中间件串联在一起

```go
// 基础中间件结构
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 处理器之前的操作
        fmt.Println("处理器之前")
        
        // 调用下一个处理器
        next.ServeHTTP(w, r)
        
        // 处理器之后的操作
        fmt.Println("处理器之后")
    })
}
```

### http.Handler 接口

Go HTTP 服务器的核心是 `http.Handler` 接口：

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

而 `http.HandlerFunc` 将普通函数适配到此接口：

```go
type HandlerFunc func(ResponseWriter, *Request)

func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
    f(w, r)
}
```

### 中间件链式调用

中间件可以串联起来形成一个处理管道：

```go
func main() {
    // 创建新的 mux（路由器）
    mux := http.NewServeMux()
    mux.HandleFunc("/api", apiHandler)
    
    // 使用中间件链包装 mux
    handler := loggingMiddleware(
        authenticationMiddleware(
            rateLimitMiddleware(mux),
        ),
    )
    
    http.ListenAndServe(":8080", handler)
}
```

### 认证中间件模式

#### 基本认证

```go
func basicAuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 从请求头获取凭证
        username, password, ok := r.BasicAuth()
        
        // 检查凭证
        if !ok || !checkCredentials(username, password) {
            w.Header().Set("WWW-Authenticate", `Basic realm="Restricted"`)
            http.Error(w, "未授权", http.StatusUnauthorized)
            return
        }
        
        // 将已认证用户存入上下文
        ctx := context.WithValue(r.Context(), userContextKey, username)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

#### Token 认证

```go
func tokenAuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 从头信息中获取 token
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" {
            http.Error(w, "需要授权头", http.StatusUnauthorized)
            return
        }
        
        // 检查格式（Bearer token）
        parts := strings.SplitN(authHeader, " ", 2)
        if len(parts) != 2 || parts[0] != "Bearer" {
            http.Error(w, "无效的授权格式", http.StatusUnauthorized)
            return
        }
        
        token := parts[1]
        
        // 验证 token（取决于你的 token 系统）
        user, err := validateToken(token)
        if err != nil {
            http.Error(w, "无效的 token", http.StatusUnauthorized)
            return
        }
        
        // 将用户存入上下文
        ctx := context.WithValue(r.Context(), userContextKey, user)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

### HTTP 请求中的 Context

Go 的 `context` 包允许在中间件和处理器之间传递请求范围的值：

```go
// 定义上下文键类型以避免冲突
type contextKey string

// 定义特定键
const userContextKey contextKey = "user"

// 在上下文中存储值
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 创建带值的新上下文
        ctx := context.WithValue(r.Context(), userContextKey, "john")
        
        // 使用更新后的上下文调用下一个处理器
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// 从上下文中检索值
func handler(w http.ResponseWriter, r *http.Request) {
    user, ok := r.Context().Value(userContextKey).(string)
    if !ok {
        // 处理缺失值的情况
        return
    }
    fmt.Fprintf(w, "你好，%s", user)
}
```

### JWT 认证

JSON Web Tokens (JWT) 是 Web 应用程序中常见的认证方法：

```go
// 使用流行的 Go JWT 库 (github.com/golang-jwt/jwt)
import "github.com/golang-jwt/jwt/v4"

// 创建 JWT token
func createToken(username string, secret []byte) (string, error) {
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "username": username,
        "exp":      time.Now().Add(time.Hour * 24).Unix(),
    })
    
    return token.SignedString(secret)
}

// 验证 JWT token
func verifyToken(tokenString string, secret []byte) (jwt.MapClaims, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        // 验证签名方法
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("不支持的签名方法: %v", token.Header["alg"])
        }
        return secret, nil
    })
    
    if err != nil {
        return nil, err
    }
    
    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        return claims, nil
    }
    
    return nil, fmt.Errorf("无效的 token")
}

// JWT 中间件
func jwtMiddleware(secret []byte) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // 从头信息中获取 token
            authHeader := r.Header.Get("Authorization")
            if authHeader == "" {
                http.Error(w, "需要授权头", http.StatusUnauthorized)
                return
            }
            
            // 提取 token
            parts := strings.SplitN(authHeader, " ", 2)
            if len(parts) != 2 || parts[0] != "Bearer" {
                http.Error(w, "无效的授权格式", http.StatusUnauthorized)
                return
            }
            
            tokenString := parts[1]
            
            // 验证 token
            claims, err := verifyToken(tokenString, secret)
            if err != nil {
                http.Error(w, "无效的 token: "+err.Error(), http.StatusUnauthorized)
                return
            }
            
            // 将用户存入上下文
            username := claims["username"].(string)
            ctx := context.WithValue(r.Context(), userContextKey, username)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

### 测试中间件

使用 `httptest` 包测试中间件和 HTTP 处理器在 Go 中非常简单：

```go
func TestAuthMiddleware(t *testing.T) {
    // 创建测试处理器
    testHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        user := r.Context().Value(userContextKey).(string)
        fmt.Fprintf(w, "用户: %s", user)
    })
    
    // 使用中间件包装
    handler := authMiddleware(testHandler)
    
    // 创建测试请求
    req := httptest.NewRequest("GET", "/", nil)
    req.Header.Set("Authorization", "Bearer valid-token")
    
    // 创建记录器以捕获响应
    rr := httptest.NewRecorder()
    
    // 处理请求
    handler.ServeHTTP(rr, req)
    
    // 检查状态码
    if status := rr.Code; status != http.StatusOK {
        t.Errorf("处理器返回了错误的状态码: 实际 %v 期望 %v", status, http.StatusOK)
    }
    
    // 检查响应体
    expected := "用户: john"
    if rr.Body.String() != expected {
        t.Errorf("处理器返回了意外的响应体: 实际 %v 期望 %v", rr.Body.String(), expected)
    }
}
```

## HTTP 中间件的最佳实践

1. **使用 context 存储请求范围的值**：存储认证数据、请求 ID 等。
2. **保持中间件职责单一**：每个中间件应只负责一项任务。
3. **优雅地处理错误**：返回适当的 HTTP 状态码和错误信息。
4. **不要忘记安全头**：设置如 `X-XSS-Protection`、`Content-Security-Policy` 等头。
5. **记录请求和错误**：包含日志中间件以便调试。

## 进一步阅读

- [Go Web 示例：中间件](https://gowebexamples.com/middleware/)
- [Go Web 示例：JSON Web Tokens](https://gowebexamples.com/jwt/)
- [Context 包文档](https://pkg.go.dev/context)
- [Effective Go：Web 服务器](https://golang.org/doc/effective_go#web_server)