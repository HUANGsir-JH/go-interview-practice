# 并发网络内容聚合器学习资料

## Go 中的高级并发模式

本挑战聚焦于实现一个并发获取和处理网络内容的系统，采用高级并发模式、上下文处理和速率限制。

### 并发与并行

- **并发**：将程序结构化为独立执行的组件
- **并行**：同时执行多个计算

Go 通过 goroutine 和运行时调度器支持两者：

```go
// 并发运行多个任务
go task1()
go task2()
go task3()
```

### 网络爬取基础

在 Go 中获取网络内容：

```go
import (
    "io"
    "net/http"
)

func fetchURL(url string) (string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }
    
    return string(body), nil
}
```

### 高级上下文使用

`context` 包有助于管理取消、截止时间和请求值：

```go
import (
    "context"
    "net/http"
    "time"
)

// 带超时
func fetchWithTimeout(url string, timeout time.Duration) (string, error) {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()
    
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return "", err
    }
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    return string(body), err
}

// 带取消
func fetchMultipleURLs(urls []string) <-chan string {
    ctx, cancel := context.WithCancel(context.Background())
    results := make(chan string)
    
    // 为每个 URL 启动协程
    for _, url := range urls {
        go func(u string) {
            resp, err := fetchWithContext(ctx, u)
            if err != nil {
                cancel() // 若其中一个失败则取消所有其他请求
                return
            }
            results <- resp
        }(url)
    }
    
    return results
}
```

### 上下文值

通过调用链传递请求范围的值：

```go
// 定义自定义键类型以避免冲突
type contextKey string

const (
    userKey   contextKey = "user"
    requestID contextKey = "request-id"
)

// 在上下文中存储值
func enrichContext(ctx context.Context) context.Context {
    ctx = context.WithValue(ctx, userKey, "admin")
    ctx = context.WithValue(ctx, requestID, uuid.New().String())
    return ctx
}

// 从上下文中检索值
func processWithContext(ctx context.Context, url string) {
    user, ok := ctx.Value(userKey).(string)
    if !ok {
        user = "anonymous"
    }
    
    id := ctx.Value(requestID)
    
    // 使用这些值
    log.Printf("用户 %s (请求 %v) 正在处理 URL: %s", user, id, url)
}
```

### 速率限制

控制请求速率以避免压垮服务器或触达 API 限制：

```go
import (
    "context"
    "golang.org/x/time/rate"
    "net/http"
)

// 带速率限制的客户端
type RateLimitedClient struct {
    client  *http.Client
    limiter *rate.Limiter
}

func NewRateLimitedClient(rps float64, burst int) *RateLimitedClient {
    return &RateLimitedClient{
        client:  &http.Client{},
        limiter: rate.NewLimiter(rate.Limit(rps), burst),
    }
}

func (c *RateLimitedClient) Do(req *http.Request) (*http.Response, error) {
    // 等待速率限制器
    err := c.limiter.Wait(req.Context())
    if err != nil {
        return nil, err
    }
    
    // 执行请求
    return c.client.Do(req)
}

// 使用示例
client := NewRateLimitedClient(1.0, 5) // 每秒 1 次请求，突发 5 次
```

### 工作池

限制并发操作的数量：

```go
func WorkerPool(urls []string, numWorkers int) <-chan string {
    var wg sync.WaitGroup
    results := make(chan string)
    
    // 创建任务通道
    jobs := make(chan string, len(urls))
    
    // 启动工作协程
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for url := range jobs {
                content, err := fetchURL(url)
                if err != nil {
                    log.Printf("获取 %s 时出错: %v", url, err)
                    continue
                }
                results <- content
            }
        }()
    }
    
    // 将任务发送给工作协程
    for _, url := range urls {
        jobs <- url
    }
    close(jobs)
    
    // 当所有工作协程完成时关闭结果通道
    go func() {
        wg.Wait()
        close(results)
    }()
    
    return results
}
```

### 扇出、扇入模式

分阶段处理数据，分配工作并收集结果：

```go
func fetch(urls <-chan string) <-chan *Result {
    results := make(chan *Result)
    
    go func() {
        defer close(results)
        for url := range urls {
            res, err := fetchURL(url)
            results <- &Result{URL: url, Content: res, Error: err}
        }
    }()
    
    return results
}

func process(results <-chan *Result) <-chan *ProcessedResult {
    processed := make(chan *ProcessedResult)
    
    go func() {
        defer close(processed)
        for res := range results {
            if res.Error != nil {
                continue
            }
            
            // 处理内容
            data := extractData(res.Content)
            processed <- &ProcessedResult{URL: res.URL, Data: data}
        }
    }()
    
    return processed
}

func merge(channels ...<-chan *ProcessedResult) <-chan *ProcessedResult {
    var wg sync.WaitGroup
    merged := make(chan *ProcessedResult)
    
    // 将通道中的数据复制到合并通道的函数
    output := func(c <-chan *ProcessedResult) {
        defer wg.Done()
        for val := range c {
            merged <- val
        }
    }
    
    // 为每个输入通道启动输出协程
    wg.Add(len(channels))
    for _, c := range channels {
        go output(c)
    }
    
    // 当所有输出协程完成后关闭合并通道
    go func() {
        wg.Wait()
        close(merged)
    }()
    
    return merged
}

// 使用示例
func main() {
    urls := make(chan string)
    
    // 分发工作给多个获取器（扇出）
    var fetchers []<-chan *Result
    for i := 0; i < 5; i++ {
        fetchers = append(fetchers, fetch(urls))
    }
    
    // 合并结果（扇入）
    results := mergeFetchResults(fetchers...)
    
    // 使用多个处理器处理结果（扇出）
    var processors []<-chan *ProcessedResult
    for i := 0; i < 3; i++ {
        processors = append(processors, process(results))
    }
    
    // 合并已处理的结果（扇入）
    processed := merge(processors...)
    
    // 发送 URL 进行处理
    go func() {
        for _, url := range targetURLs {
            urls <- url
        }
        close(urls)
    }()
    
    // 收集结果
    for p := range processed {
        fmt.Printf("URL: %s, 数据: %v\n", p.URL, p.Data)
    }
}
```

### 并发代码中的错误处理

几种处理并发操作中错误的策略：

#### 1. 通过通道返回错误

```go
type Result struct {
    Value string
    Error error
}

func fetchAsync(url string) <-chan Result {
    result := make(chan Result, 1)
    
    go func() {
        resp, err := http.Get(url)
        if err != nil {
            result <- Result{Error: err}
            close(result)
            return
        }
        defer resp.Body.Close()
        
        body, err := io.ReadAll(resp.Body)
        result <- Result{Value: string(body), Error: err}
        close(result)
    }()
    
    return result
}
```

#### 2. 使用 errgroup 实现协调的错误处理

```go
import "golang.org/x/sync/errgroup"

func fetchAll(urls []string) ([]string, error) {
    var g errgroup.Group
    results := make([]string, len(urls))
    
    for i, url := range urls {
        i, url := i, url // 为闭包创建局部变量
        
        g.Go(func() error {
            resp, err := http.Get(url)
            if err != nil {
                return err
            }
            defer resp.Body.Close()
            
            body, err := io.ReadAll(resp.Body)
            if err != nil {
                return err
            }
            
            results[i] = string(body)
            return nil
        })
    }
    
    // 等待所有 HTTP 获取完成
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return results, nil
}
```

### 重试逻辑

实现带退避的重试以处理瞬时故障：

```go
func fetchWithRetry(url string, maxRetries int) (string, error) {
    var (
        body  string
        err   error
        sleep time.Duration = 100 * time.Millisecond
    )
    
    for i := 0; i <= maxRetries; i++ {
        if i > 0 {
            log.Printf("第 %d 次重试 %s，等待 %v", i, url, sleep)
            time.Sleep(sleep)
            sleep *= 2 // 指数退避
        }
        
        body, err = fetchURL(url)
        if err == nil {
            return body, nil
        }
        
        // 检查是否应重试
        if !isRetryable(err) {
            return "", err
        }
    }
    
    return "", fmt.Errorf("重试 %d 次后仍失败: %w", maxRetries, err)
}

func isRetryable(err error) bool {
    // 检查网络错误、429 Too Many Requests、5xx 服务器错误
    var netErr net.Error
    if errors.As(err, &netErr) && netErr.Temporary() {
        return true
    }
    
    var httpErr *url.Error
    if errors.As(err, &httpErr) {
        return httpErr.Timeout() || isRetryableStatusCode(httpErr)
    }
    
    return false
}
```

### 熔断器模式

在出现过多错误后“断开电路”，防止级联故障：

```go
type CircuitBreaker struct {
    maxFailures     int
    failureCount    int
    resetTimeout    time.Duration
    lastFailureTime time.Time
    mu              sync.Mutex
}

func NewCircuitBreaker(maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        maxFailures:  maxFailures,
        resetTimeout: resetTimeout,
    }
}

func (cb *CircuitBreaker) Execute(op func() error) error {
    cb.mu.Lock()
    
    // 检查电路是否已打开（最近出现太多失败）
    if cb.failureCount >= cb.maxFailures {
        if time.Since(cb.lastFailureTime) > cb.resetTimeout {
            // 超时后重置
            cb.failureCount = 0
        } else {
            cb.mu.Unlock()
            return fmt.Errorf("电路已打开：失败次数过多")
        }
    }
    
    cb.mu.Unlock()
    
    // 执行操作
    err := op()
    
    if err != nil {
        cb.mu.Lock()
        cb.failureCount++
        cb.lastFailureTime = time.Now()
        cb.mu.Unlock()
    }
    
    return err
}
```

### 处理外部 API 依赖

在从外部 API 聚合内容时，考虑以下最佳实践：

1. **超时**：为所有请求设置适当的超时时间
2. **缓存**：缓存响应以减少负载并提高性能
3. **回退**：当服务不可用时提供备用内容
4. **重试**：对瞬时故障实现带退避的重试
5. **熔断器**：防止级联故障

```go
// 结合上述模式的简化内容获取器
type ContentFetcher struct {
    client          *http.Client
    cache           map[string]CachedResponse
    cacheMu         sync.RWMutex
    circuitBreakers map[string]*CircuitBreaker
    rateLimiters    map[string]*rate.Limiter
}

func (f *ContentFetcher) FetchContent(ctx context.Context, url string) (string, error) {
    // 先检查缓存
    f.cacheMu.RLock()
    if cached, ok := f.cache[url]; ok && !cached.Expired() {
        f.cacheMu.RUnlock()
        return cached.Content, nil
    }
    f.cacheMu.RUnlock()
    
    // 检查域名是否受速率限制
    domain := extractDomain(url)
    if limiter, ok := f.rateLimiters[domain]; ok {
        if err := limiter.Wait(ctx); err != nil {
            return "", err
        }
    }
    
    // 检查熔断器
    if breaker, ok := f.circuitBreakers[domain]; ok {
        var content string
        err := breaker.Execute(func() error {
            var fetchErr error
            content, fetchErr = f.fetchWithRetry(ctx, url, 3)
            return fetchErr
        })
        
        if err != nil {
            return f.getFallbackContent(url), nil
        }
        
        // 缓存成功响应
        f.cacheResponse(url, content)
        return content, nil
    }
    
    // 普通获取并重试
    content, err := f.fetchWithRetry(ctx, url, 3)
    if err != nil {
        return f.getFallbackContent(url), nil
    }
    
    // 缓存成功响应
    f.cacheResponse(url, content)
    return content, nil
}
```

## 进一步阅读

- [Go 并发模式](https://talks.golang.org/2012/concurrency.slide)
- [Go 高级并发模式](https://talks.golang.org/2013/advconc.slide)
- [Context 包文档](https://pkg.go.dev/context)
- [Go 中的速率限制](https://pkg.go.dev/golang.org/x/time/rate)
- [Errgroup 包](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [熔断器模式](https://martinfowler.com/bliki/CircuitBreaker.html)