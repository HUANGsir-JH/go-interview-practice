# 挑战 11 提示：并发网页内容聚合器

## 提示 1：理解核心结构
从实现基本的 ContentAggregator 结构体开始，包含必要的字段：
```go
type ContentAggregator struct {
    fetcher         ContentFetcher
    processor       ContentProcessor
    workerCount     int
    requestLimiter  *rate.Limiter  // 用于速率限制
    wg              sync.WaitGroup
    shutdown        chan struct{}
    shutdownOnce    sync.Once
}
```

## 提示 2：速率限制实现
使用 Go 的 `golang.org/x/time/rate` 包实现速率限制：
```go
import "golang.org/x/time/rate"

// 在构造函数中
requestLimiter := rate.NewLimiter(rate.Limit(requestsPerSecond), 1)

// 发起请求前
err := requestLimiter.Wait(ctx)
if err != nil {
    return err // 上下文被取消或超时
}
```

## 提示 3：工作池模式
创建一个从通道处理任务的工作池：
```go
func (ca *ContentAggregator) workerPool(ctx context.Context, jobs <-chan string, results chan<- ProcessedData, errors chan<- error) {
    for i := 0; i < ca.workerCount; i++ {
        ca.wg.Add(1)
        go func() {
            defer ca.wg.Done()
            for {
                select {
                case url, ok := <-jobs:
                    if !ok {
                        return // 通道已关闭
                    }
                    // 在此处处理 URL
                case <-ctx.Done():
                    return
                }
            }
        }()
    }
}
```

## 提示 4：扇出、扇入模式
将 URL 分发给工作线程并收集结果：
```go
func (ca *ContentAggregator) FetchAndProcess(ctx context.Context, urls []string) ([]ProcessedData, error) {
    jobs := make(chan string, len(urls))
    results := make(chan ProcessedData, len(urls))
    errors := make(chan error, len(urls))
    
    // 启动工作线程
    ca.workerPool(ctx, jobs, results, errors)
    
    // 发送任务
    go func() {
        defer close(jobs)
        for _, url := range urls {
            select {
            case jobs <- url:
            case <-ctx.Done():
                return
            }
        }
    }()
    
    // 收集结果
    // 实现在此...
}
```

## 提示 5：上下文传播与错误处理
始终向下传递上下文并处理取消操作：
```go
// 在工作线程处理中
content, err := ca.fetcher.Fetch(ctx, url)
if err != nil {
    select {
    case errors <- fmt.Errorf("获取失败：%s: %w", url, err):
    case <-ctx.Done():
    }
    return
}

processedData, err := ca.processor.Process(ctx, content)
if err != nil {
    select {
    case errors <- fmt.Errorf("处理失败：%s: %w", url, err):
    case <-ctx.Done():
    }
    return
}
```

## 提示 6：优雅关闭
在关闭方法中实现适当的清理：
```go
func (ca *ContentAggregator) Shutdown() error {
    ca.shutdownOnce.Do(func() {
        close(ca.shutdown)
        ca.wg.Wait() // 等待所有工作线程完成
    })
    return nil
}
```

## 提示 7：结果收集模式
使用单独的 goroutine 收集结果并处理完成信号：
```go
// 创建用于收集结果的通道
var allResults []ProcessedData
var allErrors []error

done := make(chan struct{})
go func() {
    defer close(done)
    for i := 0; i < len(urls); i++ {
        select {
        case result := <-results:
            allResults = append(allResults, result)
        case err := <-errors:
            allErrors = append(allErrors, err)
        case <-ctx.Done():
            return
        }
    }
}()

// 等待完成或上下文取消
select {
case <-done:
    // 所有 URL 已处理
case <-ctx.Done():
    return nil, ctx.Err()
}
```

## 需要记住的关键概念：
- **上下文**：始终传递上下文并检查是否被取消
- **通道**：使用带缓冲的通道以避免阻塞
- **WaitGroup**：协调 goroutine 的完成
- **速率限制**：遵守速率限制，避免过度冲击服务器
- **错误处理**：收集并返回有意义的错误
- **资源清理**：始终关闭通道并等待 goroutine 结束