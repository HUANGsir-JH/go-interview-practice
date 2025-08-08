# 挑战30：上下文管理实现提示

## 提示1：上下文创建与取消
实现支持取消的基本上下文创建：
```go
import (
    "context"
    "errors"
    "sync"
    "time"
)

type ContextManager struct {
    // 添加任何用于状态管理的字段
}

func NewContextManager() *ContextManager {
    return &ContextManager{}
}

func (cm *ContextManager) CreateCancellableContext(parent context.Context) (context.Context, context.CancelFunc) {
    return context.WithCancel(parent)
}

func (cm *ContextManager) CreateTimeoutContext(parent context.Context, timeout time.Duration) (context.Context, context.CancelFunc) {
    return context.WithTimeout(parent, timeout)
}
```

## 提示2：值存储与获取
安全地实现上下文值操作：
```go
func (cm *ContextManager) AddValue(parent context.Context, key, value interface{}) context.Context {
    return context.WithValue(parent, key, value)
}

func (cm *ContextManager) GetValue(ctx context.Context, key interface{}) (interface{}, bool) {
    value := ctx.Value(key)
    if value == nil {
        return nil, false
    }
    return value, true
}

// 类型安全值获取示例
func getStringValue(ctx context.Context, key interface{}) (string, bool) {
    value := ctx.Value(key)
    if str, ok := value.(string); ok {
        return str, true
    }
    return "", false
}
```

## 提示3：支持上下文的任务执行
以适当的取消处理方式执行任务：
```go
func (cm *ContextManager) ExecuteWithContext(ctx context.Context, task func() error) error {
    // 接收任务结果的通道
    resultChan := make(chan error, 1)
    
    // 在goroutine中执行任务
    go func() {
        defer close(resultChan)
        if err := task(); err != nil {
            resultChan <- err
        }
    }()
    
    // 等待任务完成或上下文被取消
    select {
    case <-ctx.Done():
        return ctx.Err()
    case err := <-resultChan:
        return err
    }
}

// 带超时的替代实现
func (cm *ContextManager) ExecuteWithContextTimeout(ctx context.Context, task func() error, timeout time.Duration) error {
    timeoutCtx, cancel := context.WithTimeout(ctx, timeout)
    defer cancel()
    
    return cm.ExecuteWithContext(timeoutCtx, task)
}
```

## 提示4：等待操作
实现支持上下文取消的等待功能：
```go
func (cm *ContextManager) WaitForCompletion(ctx context.Context, duration time.Duration) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(duration):
        return nil
    }
}

// 带进度跟踪的增强等待
func (cm *ContextManager) WaitWithProgress(ctx context.Context, duration time.Duration, progressCallback func(elapsed time.Duration)) error {
    ticker := time.NewTicker(duration / 10) // 10% 间隔
    defer ticker.Stop()
    
    start := time.Now()
    deadline := start.Add(duration)
    
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case now := <-ticker.C:
            if now.After(deadline) {
                return nil
            }
            if progressCallback != nil {
                progressCallback(now.Sub(start))
            }
        }
    }
}
```

## 提示5：模拟工作函数
实现带取消检查的工作模拟：
```go
func SimulateWork(ctx context.Context, workDuration time.Duration, description string) error {
    if description == "" {
        description = "work"
    }
    
    // 将工作分成小块以允许取消
    chunkDuration := time.Millisecond * 100
    chunks := int(workDuration / chunkDuration)
    remainder := workDuration % chunkDuration
    
    for i := 0; i < chunks; i++ {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(chunkDuration):
            // 继续工作
        }
    }
    
    // 处理剩余时间
    if remainder > 0 {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(remainder):
            // 工作完成
        }
    }
    
    return nil
}

// 带进度报告的工作模拟
func SimulateWorkWithProgress(ctx context.Context, workDuration time.Duration, description string, progressFn func(float64)) error {
    start := time.Now()
    chunkDuration := time.Millisecond * 50
    
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(chunkDuration):
            elapsed := time.Since(start)
            if elapsed >= workDuration {
                if progressFn != nil {
                    progressFn(1.0)
                }
                return nil
            }
            
            if progressFn != nil {
                progress := float64(elapsed) / float64(workDuration)
                progressFn(progress)
            }
        }
    }
}
```

## 提示6：具有上下文感知的项目处理
实现批量处理并支持项目间的取消：
```go
func ProcessItems(ctx context.Context, items []string) ([]string, error) {
    if len(items) == 0 {
        return []string{}, nil
    }
    
    results := make([]string, 0, len(items))
    
    for i, item := range items {
        // 在处理每个项目前检查是否取消
        select {
        case <-ctx.Done():
            return results, ctx.Err()
        default:
            // 继续处理
        }
        
        // 模拟项目处理时间
        processingTime := time.Millisecond * 50
        if err := SimulateWork(ctx, processingTime, fmt.Sprintf("处理项目 %d", i)); err != nil {
            return results, err
        }
        
        // 转换项目（示例：转为大写）
        processed := fmt.Sprintf("已处理_%s", strings.ToUpper(item))
        results = append(results, processed)
    }
    
    return results, nil
}

// 并发处理项目并支持上下文
func ProcessItemsConcurrently(ctx context.Context, items []string, maxWorkers int) ([]string, error) {
    if len(items) == 0 {
        return []string{}, nil
    }
    
    if maxWorkers <= 0 {
        maxWorkers = 1
    }
    
    type result struct {
        index int
        value string
        err   error
    }
    
    itemChan := make(chan struct{ index int; item string }, len(items))
    resultChan := make(chan result, len(items))
    
    // 发送待处理项目
    for i, item := range items {
        itemChan <- struct{ index int; item string }{i, item}
    }
    close(itemChan)
    
    // 启动工作协程
    var wg sync.WaitGroup
    for i := 0; i < maxWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for work := range itemChan {
                select {
                case <-ctx.Done():
                    resultChan <- result{work.index, "", ctx.Err()}
                    return
                default:
                    // 处理项目
                    processed := fmt.Sprintf("已处理_%s", strings.ToUpper(work.item))
                    resultChan <- result{work.index, processed, nil}
                }
            }
        }()
    }
    
    // 所有工作协程完成后关闭结果通道
    go func() {
        wg.Wait()
        close(resultChan)
    }()
    
    // 收集结果
    results := make([]string, len(items))
    for result := range resultChan {
        if result.err != nil {
            return nil, result.err
        }
        results[result.index] = result.value
    }
    
    return results, nil
}
```

## 提示7：高级上下文模式
实现高级上下文管理模式：
```go
// 带多个值的上下文
func (cm *ContextManager) CreateContextWithMultipleValues(parent context.Context, values map[interface{}]interface{}) context.Context {
    ctx := parent
    for key, value := range values {
        ctx = context.WithValue(ctx, key, value)
    }
    return ctx
}

// 带清理的超时执行
func (cm *ContextManager) ExecuteWithCleanup(ctx context.Context, task func() error, cleanup func()) error {
    if cleanup != nil {
        defer cleanup()
    }
    
    return cm.ExecuteWithContext(ctx, task)
}

// 链式执行多个操作并携带上下文
func (cm *ContextManager) ChainOperations(ctx context.Context, operations []func(context.Context) error) error {
    for i, op := range operations {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := op(ctx); err != nil {
                return fmt.Errorf("操作 %d 失败: %w", i, err)
            }
        }
    }
    return nil
}

// 限速上下文操作
func (cm *ContextManager) RateLimitedExecution(ctx context.Context, tasks []func() error, rate time.Duration) error {
    ticker := time.NewTicker(rate)
    defer ticker.Stop()
    
    for i, task := range tasks {
        if i > 0 { // 第一个任务不等待
            select {
            case <-ctx.Done():
                return ctx.Err()
            case <-ticker.C:
                // 继续下一个任务
            }
        }
        
        if err := cm.ExecuteWithContext(ctx, task); err != nil {
            return fmt.Errorf("任务 %d 失败: %w", i, err)
        }
    }
    
    return nil
}
```

## 关键上下文管理概念：
- **上下文取消**：使用 `context.WithCancel` 实现手动取消
- **上下文超时**：使用 `context.WithTimeout` 和 `context.WithDeadline`
- **上下文值**：使用 `context.WithValue` 存储请求范围的数据
- **Goroutine 协调**：使用通道配合上下文实现取消控制
- **Select 语句**：在 select 语句中始终检查 `ctx.Done()`
- **错误处理**：区分 `context.Canceled` 和 `context.DeadlineExceeded`
- **资源清理**：使用 defer 语句确保正确清理