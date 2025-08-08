[查看排行榜](SCOREBOARD.md)

# 挑战 29：速率限制器实现

## 问题描述

实现一个全面的速率限制系统，用于控制请求或操作的速率。本挑战聚焦于理解速率限制算法、并发控制，并实现能够处理高吞吐场景的健壮系统。

## 要求

1. 实现 `RateLimiter` 接口，包含以下方法：
   - `Allow() bool`：如果请求被允许则返回 true，否则返回 false（已限流）
   - `AllowN(n int) bool`：如果允许 n 个请求则返回 true，否则返回 false（已限流）
   - `Wait(ctx context.Context) error`：阻塞直到请求可被处理（或上下文超时）
   - `WaitN(ctx context.Context, n int) error`：阻塞直到 n 个请求可被处理
   - `Limit() int`：返回当前速率限制（每秒请求数）
   - `Burst() int`：返回当前突发容量
   - `Reset()`：重置速率限制器状态

2. 实现以下速率限制算法：
   - **令牌桶**：具有可配置速率和突发容量的经典算法
   - **滑动窗口**：具有可配置窗口大小的更精确的速率限制
   - **固定窗口**：基于计数器的简单速率限制，使用固定时间窗口

3. 实现一个 `RateLimiterFactory`，用于创建不同类型的速率限制器：
   - 支持不同算法（令牌桶、滑动窗口、固定窗口）
   - 可配置参数（速率、突发容量、窗口大小）
   - 线程安全实现以支持并发使用

4. 实现高级功能：
   - **分布式速率限制**：支持跨多个实例的速率限制
   - **自适应速率限制**：根据系统负载动态调整速率限制
   - **速率限制中间件**：适用于 Web 应用程序的 HTTP 中间件
   - **指标收集**：跟踪速率限制器的统计信息和性能

## 函数签名

```go
// 核心速率限制器接口
type RateLimiter interface {
    Allow() bool
    AllowN(n int) bool
    Wait(ctx context.Context) error
    WaitN(ctx context.Context, n int) error
    Limit() int
    Burst() int
    Reset()
}

// 速率限制器类型
type TokenBucketLimiter struct {
    // 实现字段
}

type SlidingWindowLimiter struct {
    // 实现字段
}

type FixedWindowLimiter struct {
    // 实现字段
}

// 用于创建速率限制器的工厂
type RateLimiterFactory struct{}

type RateLimiterConfig struct {
    Algorithm    string // "token_bucket", "sliding_window", "fixed_window"
    Rate         int    // 每秒请求数
    Burst        int    // 最大突发容量
    WindowSize   time.Duration // 滑动窗口大小
}

// 构造函数
func NewTokenBucketLimiter(rate int, burst int) RateLimiter
func NewSlidingWindowLimiter(rate int, windowSize time.Duration) RateLimiter
func NewFixedWindowLimiter(rate int, windowSize time.Duration) RateLimiter
func NewRateLimiterFactory() *RateLimiterFactory
func (f *RateLimiterFactory) CreateLimiter(config RateLimiterConfig) (RateLimiter, error)

// 高级功能
type DistributedRateLimiter struct {
    // 分布式场景下的实现
}

type AdaptiveRateLimiter struct {
    // 自适应速率限制的实现
}

// HTTP 中间件
func RateLimitMiddleware(limiter RateLimiter) func(http.Handler) http.Handler

// 指标
type RateLimiterMetrics struct {
    TotalRequests   int64
    AllowedRequests int64
    DeniedRequests  int64
    AverageWaitTime time.Duration
}

func (rl RateLimiter) GetMetrics() RateLimiterMetrics
```

## 算法说明

### 令牌桶算法
- 以固定速率向桶中添加令牌
- 每个请求消耗一个或多个令牌
- 如果可用令牌不足，则请求被限流
- 突发容量允许临时流量激增

### 滑动窗口算法
- 维护最近请求的滑动时间窗口
- 比固定窗口更准确，不会受到边界效应影响
- 在窗口边界处平滑处理流量激增

### 固定窗口算法
- 简单计数器，在固定间隔重置
- 快速且内存效率高
- 可能在窗口边界处允许突发流量

## 约束条件

- 所有速率限制器必须支持并发使用（线程安全）
- 对无效配置应实现适当的错误处理
- 阻塞操作需支持上下文取消
- 在高吞吐场景下应具备高效的内存使用
- 支持定时操作的可配置精度

## 示例用法

### 基础用法

```go
// 创建一个令牌桶速率限制器（10次请求/秒，突发容量为5）
limiter := NewTokenBucketLimiter(10, 5)

// 检查请求是否被允许
if limiter.Allow() {
    fmt.Println("请求允许")
    // 处理请求
} else {
    fmt.Println("请求被限流")
    // 处理限流情况
}

// 等待请求被允许（带超时）
ctx, cancel := context.WithTimeout(context.Background(), time.Second)
defer cancel()

if err := limiter.Wait(ctx); err != nil {
    fmt.Printf("请求超时: %v\n", err)
} else {
    fmt.Println("等待后请求已处理")
}
```

### 工厂用法

```go
factory := NewRateLimiterFactory()

config := RateLimiterConfig{
    Algorithm:  "sliding_window",
    Rate:       100,
    WindowSize: time.Minute,
}

limiter, err := factory.CreateLimiter(config)
if err != nil {
    log.Fatal(err)
}

// 使用速率限制器
for i := 0; i < 200; i++ {
    if limiter.Allow() {
        fmt.Printf("请求 %d 允许\n", i+1)
    } else {
        fmt.Printf("请求 %d 被限流\n", i+1)
    }
    time.Sleep(10 * time.Millisecond)
}
```

### HTTP 中间件用法

```go
limiter := NewTokenBucketLimiter(100, 10) // 100 请求/秒，突发容量为10

mux := http.NewServeMux()
mux.HandleFunc("/api/endpoint", func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("请求已处理"))
})

// 应用速率限制中间件
handler := RateLimitMiddleware(limiter)(mux)

server := &http.Server{
    Addr:    ":8080",
    Handler: handler,
}

log.Println("服务器在 :8080 启动")
server.ListenAndServe()
```

### 带指标的高级用法

```go
limiter := NewTokenBucketLimiter(50, 10)

// 模拟负载
for i := 0; i < 1000; i++ {
    limiter.Allow()
    time.Sleep(time.Millisecond)
}

// 获取指标
metrics := limiter.GetMetrics()
fmt.Printf("总请求数: %d\n", metrics.TotalRequests)
fmt.Printf("允许的请求数: %d\n", metrics.AllowedRequests)
fmt.Printf("被拒绝的请求数: %d\n", metrics.DeniedRequests)
fmt.Printf("成功率: %.2f%%\n", 
    float64(metrics.AllowedRequests)/float64(metrics.TotalRequests)*100)
```

## 性能要求

- **令牌桶**：`Allow()` 操作的时间复杂度为 O(1)
- **滑动窗口**：时间复杂度为 O(log n)，其中 n 是窗口中的请求数
- **固定窗口**：`Allow()` 操作的时间复杂度为 O(1)
- 内存使用应有限且可配置
- 支持至少 10,000 个并发 goroutine

## 测试要求

你的实现应通过以下测试：
- 每种算法的基本功能
- 多个 goroutine 的并发访问
- 阻塞操作中的上下文取消
- 不同负载模式下的速率限制准确性
- 持续负载下的内存泄漏检测
- 高吞吐场景下的性能基准测试

## 指令

- **Fork** 仓库。
- **Clone** 你的 fork 到本地机器。
- **创建** 一个以你的 GitHub 用户名命名的目录，位于 `challenge-29/submissions/` 下。
- **复制** `solution-template.go` 文件到你的提交目录。
- **实现** 所需的接口、类型和方法。
- **本地测试** 你的解决方案，运行测试文件。
- **提交** 并 **推送** 代码到你的 fork。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-29/` 目录中运行以下命令：

```bash
go test -v
```

性能测试：

```bash
go test -v -bench=.
```

竞态条件检测：

```bash
go test -v -race
```