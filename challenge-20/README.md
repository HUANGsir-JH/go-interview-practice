[查看排行榜](SCOREBOARD.md)

# 挑战 20：熔断器模式

## 问题描述

实现 **熔断器模式**，以构建能够优雅处理故障的弹性系统。熔断器监控对外部服务的调用，并在这些服务不可用时防止级联故障。

熔断器具有三种状态：
- **关闭（Closed）**：正常运行，请求通过
- **打开（Open）**：服务正在失败，请求被阻断并快速失败
- **半开（Half-Open）**：测试服务是否已恢复

你将实现一个灵活的熔断器，可以包装任何函数调用，并提供自动故障检测和恢复功能。

## 函数签名

```go
type CircuitBreaker interface {
    Call(ctx context.Context, operation func() (interface{}, error)) (interface{}, error)
    GetState() State
    GetMetrics() Metrics
}

type State int
const (
    StateClosed State = iota
    StateOpen
    StateHalfOpen
)

type Metrics struct {
    Requests          int64
    Successes         int64
    Failures          int64
    ConsecutiveFailures int64
    LastFailureTime     time.Time
}

func NewCircuitBreaker(config Config) CircuitBreaker
```

## 配置项

```go
type Config struct {
    MaxRequests      uint32        // 半开状态下允许的最大请求数
    Interval         time.Duration // 关闭状态下的统计窗口时间
    Timeout          time.Duration // 进入半开状态前等待的时间
    ReadyToTrip      func(Metrics) bool // 判断何时触发熔断的函数
    OnStateChange    func(name string, from State, to State) // 状态变化回调函数
}
```

## 要求

### 1. 状态管理
- **关闭 → 打开**：当 `ReadyToTrip` 返回 true 时
- **打开 → 半开**：经过 `Timeout` 时间后
- **半开 → 关闭**：当操作成功时
- **半开 → 打开**：当操作失败时

### 2. 请求处理
- **关闭**：允许所有请求，记录指标
- **打开**：立即拒绝请求，返回 `ErrCircuitBreakerOpen`
- **半开**：允许最多 `MaxRequests` 个请求，然后决定状态

### 3. 指标跟踪
- 统计总请求数、成功数、失败数
- 跟踪连续失败次数
- 记录最后一次失败时间
- 在状态切换到关闭时重置指标

## 示例用法

```go
// 为外部 API 调用创建熔断器
cb := NewCircuitBreaker(Config{
    MaxRequests: 3,
    Interval:    time.Minute,
    Timeout:     30 * time.Second,
    ReadyToTrip: func(m Metrics) bool {
        return m.ConsecutiveFailures >= 5
    },
})

// 使用熔断器包装 API 调用
result, err := cb.Call(ctx, func() (interface{}, error) {
    return httpClient.Get("https://api.example.com/data")
})
```

## 测试场景

你的实现将接受以下测试：

1. **正常运行**：对于成功的调用，熔断器保持关闭状态
2. **故障检测**：在连续失败后熔断器打开
3. **快速失败**：当熔断器处于打开状态时，请求立即失败
4. **恢复测试**：超时后熔断器进入半开状态
5. **完全恢复**：在半开状态下的请求成功后，熔断器关闭
6. **并发安全**：多个 goroutine 同时使用同一个熔断器

## 错误类型

```go
var (
    ErrCircuitBreakerOpen    = errors.New("熔断器已打开")
    ErrTooManyRequests      = errors.New("半开状态下请求数过多")
)
```

## 指令

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-20/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- 实现熔断器模式，包含所有必需的功能。
- 通过运行测试文件在本地测试你的解决方案。
- **Commit** 并 **push** 代码到你的仓库。
- **创建** 一个 Pull Request 提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-20/` 目录下运行以下命令：

```bash
go test -v -race
```

## 难度：🔶 中级

本挑战测试你对以下内容的理解：
- 弹性设计模式
- 状态管理和并发控制
- 错误处理策略
- 指标收集
- 线程安全编程