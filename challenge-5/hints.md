# HTTP 认证中间件的提示

## 提示 1：中间件函数签名
Go中的HTTP中间件是一个接受`http.Handler`并返回`http.Handler`的函数：
```go
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 中间件逻辑在这里
    })
}
```

## 提示 2：获取头值
从请求头中提取认证令牌：
```go
token := r.Header.Get("X-Auth-Token")
```

## 提示 3：令牌验证
检查令牌是否等于预期的secret值。如果不等于，返回401：
```go
if token != "secret" {
    http.Error(w, "Unauthorized", http.StatusUnauthorized)
    return
}
```

## 提示 4：调用下一个处理程序
如果令牌有效，调用链中的下一个处理程序：
```go
next.ServeHTTP(w, r)
```

## 提示 5：设置路由
创建包含所需端点的路由器：
```go
mux := http.NewServeMux()
mux.HandleFunc("/hello", helloHandler)
mux.HandleFunc("/secure", secureHandler)
```

## 提示 6：应用中间件
用认证中间件包装你的路由器：
```go
server := &http.Server{
    Addr:    ":8080",
    Handler: authMiddleware(mux),
}
```

## 提示 7：处理程序函数
创建简单的处理程序函数：
```go
func helloHandler(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("Hello!"))
}

func secureHandler(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("You are authorized!"))
}
```

## 提示 8：缺失头处理
如果头缺失（空字符串），将其视为无效并返回401。`Header.Get()`方法在头不存在时返回空字符串。