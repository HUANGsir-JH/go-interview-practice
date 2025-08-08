# 学习指南：Go Context 包

## 什么是 Context？

Go 中的 `context` 包提供了一种在 API 边界和 goroutine 之间传递 **取消信号**、**超时** 和 **请求范围值** 的方式。它是构建健壮、生产级应用程序最重要的包之一。

### 为什么 Context 至关重要

```go
// 无 context - 无法取消或设置超时
func fetchData() ([]byte, error) {
    resp, err := http.Get("https://api.example.com/data")
    // 如果耗时 5 分钟怎么办？根本无法取消！
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}

// 使用 context - 可取消且有时间限制
func fetchDataWithContext(ctx context.Context) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", "https://api.example.com/data", nil)
    if err != nil {
        return nil, err
    }
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err // 可能是 context.DeadlineExceeded 或 context.Canceled
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}
```

## 核心 Context 类型

### 1. 背景 Context
所有 context 的根节点 - 永远不会被取消，没有截止时间，不携带任何值。

```go
ctx := context.Background()
// 在 main()、测试或初始化中用作顶层 context
```

### 2. TODO Context
当你不确定使用哪个 context 时的占位符。

```go
ctx := context.TODO()
// 在开发阶段 context 尚不明确时使用
```

### 3. 取消 Context
可手动取消以通知 goroutine 停止工作。

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // 始终调用 cancel 以防止内存泄漏

go func() {
    select {
    case <-ctx.Done():
        fmt.Println("工作已取消:", ctx.Err())
        return
    case <-time.After(5 * time.Second):
        fmt.Println("工作已完成")
    }
}()

// 2 秒后取消
time.Sleep(2 * time.Second)
cancel() // 触发 ctx.Done()
```

### 4. 截止时间/超时 Context
在特定时间后自动取消。

```go
// WithDeadline - 在指定时间取消
deadline := time.Now().Add(30 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

// WithTimeout - 经过一段时间后取消
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
```

### 5. 值 Context
在函数调用间传递请求范围的数据。

```go
ctx := context.WithValue(context.Background(), "userID", "12345")
ctx = context.WithValue(ctx, "requestID", "req-abc-123")

// 获取值
userID := ctx.Value("userID").(string)
requestID := ctx.Value("requestID").(string)
```

## Context 模式

### 模式 1：检查取消状态

```go
func doWork(ctx context.Context) error {
    for i := 0; i < 1000; i++ {
        // 定期检查是否被取消
        select {
        case <-ctx.Done():
            return ctx.Err() // context.Canceled 或 context.DeadlineExceeded
        default:
            // 继续工作
        }
        
        // 模拟工作
        time.Sleep(10 * time.Millisecond)
        fmt.Printf("处理项目 %d\n", i)
    }
    return nil
}
```

### 模式 2：与 Goroutine 配合使用的 Context

```go
func processInParallel(ctx context.Context, items []string) error {
    errChan := make(chan error, len(items))
    
    for _, item := range items {
        go func(item string) {
            select {
            case <-ctx.Done():
                errChan <- ctx.Err()
                return
            case errChan <- processItem(item):
                return
            }
        }(item)
    }
    
    // 等待所有 goroutine 完成
    for i := 0; i < len(items); i++ {
        if err := <-errChan; err != nil {
            return err
        }
    }
    
    return nil
}
```

### 模式 3：Context 竞争

```go
func executeWithTimeout(ctx context.Context, task func() error) error {
    done := make(chan error, 1)
    
    go func() {
        done <- task()
    }()
    
    select {
    case err := <-done:
        return err // 任务先完成
    case <-ctx.Done():
        return ctx.Err() // Context 先被取消/超时
    }
}
```

## 实际应用示例

### 带请求超时的 Web 服务器

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // 为本次请求创建带超时的 context
    ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
    defer cancel()
    
    // 添加请求特定的值
    ctx = context.WithValue(ctx, "requestID", generateRequestID())
    ctx = context.WithValue(ctx, "userID", getUserID(r))
    
    // 使用 context 处理请求
    result, err := processRequest(ctx, r)
    if err != nil {
        if ctx.Err() == context.DeadlineExceeded {
            http.Error(w, "请求超时", http.StatusRequestTimeout)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    json.NewEncoder(w).Encode(result)
}

func processRequest(ctx context.Context, r *http.Request) (interface{}, error) {
    // 从 context 中提取值
    requestID := ctx.Value("requestID").(string)
    userID := ctx.Value("userID").(string)
    
    log.Printf("正在处理请求 %s 的用户 %s", requestID, userID)
    
    // 使用 context 执行数据库调用
    data, err := fetchFromDatabase(ctx, userID)
    if err != nil {
        return nil, err
    }
    
    // 使用 context 执行外部 API 调用
    enriched, err := enrichData(ctx, data)
    if err != nil {
        return nil, err
    }
    
    return enriched, nil
}
```

### 带优雅关闭的 Worker 池

```go
type WorkerPool struct {
    workers int
    jobs    chan Job
    ctx     context.Context
    cancel  context.CancelFunc
}

func NewWorkerPool(workers int) *WorkerPool {
    ctx, cancel := context.WithCancel(context.Background())
    return &WorkerPool{
        workers: workers,
        jobs:    make(chan Job, 100),
        ctx:     ctx,
        cancel:  cancel,
    }
}

func (wp *WorkerPool) Start() {
    for i := 0; i < wp.workers; i++ {
        go wp.worker(i)
    }
}

func (wp *WorkerPool) worker(id int) {
    log.Printf("Worker %d 已启动", id)
    defer log.Printf("Worker %d 已停止", id)
    
    for {
        select {
        case <-wp.ctx.Done():
            log.Printf("Worker %d 正在关闭: %v", id, wp.ctx.Err())
            return
        case job := <-wp.jobs:
            wp.processJob(job)
        }
    }
}

func (wp *WorkerPool) processJob(job Job) {
    // 为该任务创建带超时的 context
    ctx, cancel := context.WithTimeout(wp.ctx, job.Timeout)
    defer cancel()
    
    err := job.Execute(ctx)
    if err != nil {
        if ctx.Err() == context.DeadlineExceeded {
            log.Printf("任务 %s 超时", job.ID)
        } else {
            log.Printf("任务 %s 失败: %v", job.ID, err)
        }
    }
}

func (wp *WorkerPool) Shutdown() {
    wp.cancel() // 这将导致所有 worker 停止
}
```

### 带 Context 的数据库操作

```go
func getUserOrders(ctx context.Context, db *sql.DB, userID string) ([]Order, error) {
    // 创建带 context 的查询
    query := `
        SELECT id, user_id, product_name, amount, created_at 
        FROM orders 
        WHERE user_id = $1 
        ORDER BY created_at DESC
    `
    
    // 使用 context 执行查询（如果 context 被取消，则查询也会被取消）
    rows, err := db.QueryContext(ctx, query, userID)
    if err != nil {
        return nil, fmt.Errorf("查询失败: %w", err)
    }
    defer rows.Close()
    
    var orders []Order
    for rows.Next() {
        // 在处理行时检查是否被取消
        select {
        case <-ctx.Done():
            return nil, ctx.Err()
        default:
        }
        
        var order Order
        err := rows.Scan(&order.ID, &order.UserID, &order.ProductName, &order.Amount, &order.CreatedAt)
        if err != nil {
            return nil, fmt.Errorf("扫描失败: %w", err)
        }
        orders = append(orders, order)
    }
    
    return orders, nil
}
```

## Context 最佳实践

### ✅ 应该：

1. **将 context 作为第一个参数传递**
```go
func ProcessData(ctx context.Context, data []byte) error // ✅ 良好
func ProcessData(data []byte, ctx context.Context) error // ❌ 不好
```

2. **始终调用 cancel() 以防止内存泄漏**
```go
ctx, cancel := context.WithTimeout(parent, 30*time.Second)
defer cancel() // ✅ 始终这样做
```

3. **在循环和长时间操作中检查 ctx.Done()**
```go
for i := 0; i < len(items); i++ {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
    }
    processItem(items[i])
}
```

4. **使用 context 传递请求范围的值**
```go
ctx = context.WithValue(ctx, "traceID", "abc123")
ctx = context.WithValue(ctx, "userID", "user456")
```

5. **从父 context 衍生子 context**
```go
childCtx, cancel := context.WithTimeout(parentCtx, 10*time.Second)
```

### ❌ 不应该：

1. **不要将 context 存储在结构体中**（极少数例外情况除外）
```go
// ❌ 不好 - context 存储在结构体中
type Server struct {
    ctx context.Context
}

// ✅ 好 - context 作为参数传递
func (s *Server) ProcessRequest(ctx context.Context) error
```

2. **不要传递 nil context**
```go
ProcessData(nil, data) // ❌ 不好
ProcessData(context.Background(), data) // ✅ 好
```

3. **不要用 context 传递可选参数**
```go
// ❌ 不好 - 用 context 传递配置
ctx = context.WithValue(ctx, "retryCount", 3)

// ✅ 好 - 使用结构体传递配置
type Config struct {
    RetryCount int
}
func ProcessData(ctx context.Context, cfg Config) error
```

4. **不要忽略 context 取消**
```go
// ❌ 不好 - 忽略 context
func doWork(ctx context.Context) {
    for i := 0; i < 1000; i++ {
        // 未检查 context
        time.Sleep(100 * time.Millisecond)
    }
}

// ✅ 好 - 尊重 context
func doWork(ctx context.Context) error {
    for i := 0; i < 1000; i++ {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }
        time.Sleep(100 * time.Millisecond)
    }
    return nil
}
```

## 常见错误及解决方案

### 错误 1：未调用 cancel 导致内存泄漏

```go
// ❌ 内存泄漏 - 未调用 cancel
func badExample() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    // cancel() 从未被调用 - goroutine 和定时器泄漏！
    doWork(ctx)
}

// ✅ 修复 - 始终调用 cancel
func goodExample() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel() // 始终调用 cancel
    doWork(ctx)
}
```

### 错误 2：Context 值的竞态条件

```go
// ❌ 竞态条件 - 值可能改变
func badExample(ctx context.Context) {
    go func() {
        userID := ctx.Value("userID").(string) // 如果为 nil 可能 panic
        processUser(userID)
    }()
}

// ✅ 安全的值提取
func goodExample(ctx context.Context) {
    userIDValue := ctx.Value("userID")
    if userIDValue == nil {
        return // 处理缺失的值
    }
    userID, ok := userIDValue.(string)
    if !ok {
        return // 处理类型错误
    }
    
    go func() {
        processUser(userID)
    }()
}
```

### 错误 3：Context 继承问题

```go
// ❌ 不好 - 创建独立的 context
func badChain() {
    ctx1, cancel1 := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel1()
    
    ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second) // 独立！
    defer cancel2()
    
    doWork(ctx2) // 不会继承 ctx1 的取消
}

// ✅ 好 - 正确的 context 链接
func goodChain() {
    ctx1, cancel1 := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel1()
    
    ctx2, cancel2 := context.WithTimeout(ctx1, 5*time.Second) // 从 ctx1 继承
    defer cancel2()
    
    doWork(ctx2) // 当 ctx1 或 ctx2 超时时都会被取消
}
```

## 使用 Context 进行测试

```go
func TestWithTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
    defer cancel()
    
    err := doSlowWork(ctx)
    if err != context.DeadlineExceeded {
        t.Errorf("期望超时，实际得到 %v", err)
    }
}

func TestWithCancellation(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    
    go func() {
        time.Sleep(50 * time.Millisecond)
        cancel()
    }()
    
    err := doWork(ctx)
    if err != context.Canceled {
        t.Errorf("期望取消，实际得到 %v", err)
    }
}
```

## 高级 Context 模式

### 自定义 Context 类型（高级）

```go
type contextKey string

const (
    RequestIDKey contextKey = "requestID"
    UserIDKey   contextKey = "userID"
)

// 类型安全的 context 辅助函数
func WithRequestID(ctx context.Context, requestID string) context.Context {
    return context.WithValue(ctx, RequestIDKey, requestID)
}

func GetRequestID(ctx context.Context) (string, bool) {
    requestID, ok := ctx.Value(RequestIDKey).(string)
    return requestID, ok
}
```

### Context 中间件

```go
func contextMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 将请求 ID 添加到 context
        requestID := generateRequestID()
        ctx := WithRequestID(r.Context(), requestID)
        
        // 将用户信息添加到 context
        if userID := getUserFromAuth(r); userID != "" {
            ctx = context.WithValue(ctx, UserIDKey, userID)
        }
        
        // 设置响应头
        w.Header().Set("X-Request-ID", requestID)
        
        // 使用增强后的 context 调用下一个处理器
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## 性能考虑

1. **Context 开销极小** - 正常使用无需担心性能
2. **避免过度 context 链接** - 每次 WithValue 都会创建新 context
3. **谨慎使用 context 值** - 它们并非用于存储大量数据
4. **在热点路径中注意 context** - 若怀疑有问题，请进行性能分析

## 进一步学习资源

- [Go Context 包文档](https://pkg.go.dev/context)
- [Go 博客：Go 并发模式：Context](https://go.dev/blog/context)
- [Effective Go：并发](https://go.dev/doc/effective_go#concurrency)
- [Go Wiki：Context](https://github.com/golang/go/wiki/Context)

## 总结

context 包对于以下方面至关重要：
- **取消**：当不再需要工作时停止执行
- **超时**：防止操作运行过久
- **请求范围值**：跨函数边界传递数据
- **优雅关闭**：协调多个 goroutine 的清理工作

掌握这些模式，你就能编写出更健壮、更易维护的 Go 应用程序！