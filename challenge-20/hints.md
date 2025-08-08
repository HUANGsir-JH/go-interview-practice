# 挑战 20：断路器模式提示

## 提示 1：基本断路器结构
从核心结构和状态管理开始：
```go
type circuitBreaker struct {
    config     Config
    state      State
    metrics    Metrics
    mutex      sync.RWMutex
    lastTrip   time.Time
    requests   int64
}

func NewCircuitBreaker(config Config) CircuitBreaker {
    return &circuitBreaker{
        config: config,
        state:  StateClosed,
    }
}
```

## 提示 2：状态转换逻辑
实现核心的状态转换方法：
```go
func (cb *circuitBreaker) setState(newState State) {
    if cb.state == newState {
        return
    }
    
    oldState := cb.state
    cb.state = newState
    
    if cb.config.OnStateChange != nil {
        cb.config.OnStateChange("circuit-breaker", oldState, newState)
    }
    
    // 转换到关闭状态时重置指标
    if newState == StateClosed {
        cb.resetMetrics()
    }
}

func (cb *circuitBreaker) resetMetrics() {
    cb.metrics = Metrics{}
    cb.requests = 0
}
```

## 提示 3：调用方法实现模式
使用适当的锁结构化主调用方法：
```go
func (cb *circuitBreaker) Call(ctx context.Context, operation func() (interface{}, error)) (interface{}, error) {
    // 检查当前状态
    state, err := cb.checkState()
    if err != nil {
        return nil, err
    }
    
    // 根据状态执行操作
    switch state {
    case StateClosed:
        return cb.callClosed(operation)
    case StateHalfOpen:
        return cb.callHalfOpen(operation)
    case StateOpen:
        return nil, ErrCircuitBreakerOpen
    default:
        return nil, errors.New("未知的断路器状态")
    }
}
```

## 提示 4：关闭状态处理
在断路器处于关闭状态时处理请求：
```go
func (cb *circuitBreaker) callClosed(operation func() (interface{}, error)) (interface{}, error) {
    result, err := operation()
    
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    cb.metrics.Requests++
    
    if err != nil {
        cb.metrics.Failures++
        cb.metrics.ConsecutiveFailures++
        cb.metrics.LastFailureTime = time.Now()
        
        // 检查是否应该切换到打开状态
        if cb.config.ReadyToTrip(cb.metrics) {
            cb.lastTrip = time.Now()
            cb.setState(StateOpen)
        }
    } else {
        cb.metrics.Successes++
        cb.metrics.ConsecutiveFailures = 0
    }
    
    return result, err
}
```

## 提示 5：半开状态管理
在断路器处于半开状态时处理测试阶段：
```go
func (cb *circuitBreaker) callHalfOpen(operation func() (interface{}, error)) (interface{}, error) {
    cb.mutex.Lock()
    
    // 检查是否已超过半开状态下的最大请求数
    if cb.requests >= int64(cb.config.MaxRequests) {
        cb.mutex.Unlock()
        return nil, ErrTooManyRequests
    }
    
    cb.requests++
    cb.mutex.Unlock()
    
    // 执行操作
    result, err := operation()
    
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    if err != nil {
        // 半开状态下失败，返回打开状态
        cb.lastTrip = time.Now()
        cb.setState(StateOpen)
    } else {
        // 半开状态下成功，进入关闭状态
        cb.setState(StateClosed)
    }
    
    return result, err
}
```

## 提示 6：带超时逻辑的状态检查
实现带自动转换的状态检查：
```go
func (cb *circuitBreaker) checkState() (State, error) {
    cb.mutex.RLock()
    state := cb.state
    lastTrip := cb.lastTrip
    cb.mutex.RUnlock()
    
    // 如果处于打开状态，检查超时是否已过
    if state == StateOpen {
        if time.Since(lastTrip) >= cb.config.Timeout {
            cb.mutex.Lock()
            // 获取写锁后再次确认
            if cb.state == StateOpen && time.Since(cb.lastTrip) >= cb.config.Timeout {
                cb.setState(StateHalfOpen)
                state = StateHalfOpen
            } else {
                state = cb.state
            }
            cb.mutex.Unlock()
        }
    }
    
    return state, nil
}
```

## 提示 7：线程安全的指标访问
实现安全的指标获取：
```go
func (cb *circuitBreaker) GetState() State {
    cb.mutex.RLock()
    defer cb.mutex.RUnlock()
    return cb.state
}

func (cb *circuitBreaker) GetMetrics() Metrics {
    cb.mutex.RLock()
    defer cb.mutex.RUnlock()
    
    // 返回副本以避免竞态条件
    return Metrics{
        Requests:            cb.metrics.Requests,
        Successes:           cb.metrics.Successes,
        Failures:            cb.metrics.Failures,
        ConsecutiveFailures: cb.metrics.ConsecutiveFailures,
        LastFailureTime:     cb.metrics.LastFailureTime,
    }
}
```

## 提示 8：错误定义与配置验证
定义所需的错误并验证配置：
```go
var (
    ErrCircuitBreakerOpen = errors.New("断路器处于打开状态")
    ErrTooManyRequests   = errors.New("半开状态下请求数过多")
)

func validateConfig(config Config) error {
    if config.MaxRequests == 0 {
        return errors.New("MaxRequests 必须大于 0")
    }
    if config.Timeout <= 0 {
        return errors.New("Timeout 必须大于 0")
    }
    if config.ReadyToTrip == nil {
        return errors.New("ReadyToTrip 函数是必需的")
    }
    return nil
}
```

## 断路器核心概念：
- **状态管理**：在关闭/打开/半开之间谨慎地进行状态转换
- **线程安全**：使用 RWMutex 实现并发访问安全
- **超时处理**：自动从打开状态过渡到半开状态
- **指标跟踪**：统计请求、失败次数及连续失败次数
- **快速失败**：当断路器处于打开状态时立即拒绝请求
- **恢复测试**：在半开状态下限制请求数量
- **配置灵活**：支持自定义失败检测逻辑和状态变更回调