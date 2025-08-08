# 挑战29：速率限制器实现提示

## 提示1：令牌桶算法
令牌桶允许在保持平均速率限制的同时进行受控的突发流量：

**核心概念：**
- **桶**：存储令牌（容量 = 突发大小）
- **填充速率**：每秒添加的令牌数（速率限制）
- **消耗**：每次请求消耗1个或更多令牌
- **突发处理**：满桶允许临时峰值

**关键实现要点：**
- 跟踪当前令牌数量和上次填充时间
- 根据经过的时间计算应添加的令牌数
- 仅当有足够的令牌时才允许请求

```go
type TokenBucket struct {
    tokens     float64    // 当前令牌数
    capacity   float64    // 最大令牌数（突发）
    refillRate float64    // 每秒令牌数
    lastRefill time.Time  // 上次填充时间戳
}

// 根据经过的时间进行填充
tokensToAdd := elapsed.Seconds() * refillRate
tokens = min(capacity, tokens + tokensToAdd)
```
```

## 提示2：令牌桶 - 允许和等待方法
实现核心的速率限制逻辑：
```go
func (tb *TokenBucketLimiter) Allow() bool {
    return tb.AllowN(1)
}

func (tb *TokenBucketLimiter) AllowN(n int) bool {
    tb.mu.Lock()
    defer tb.mu.Unlock()
    
    tb.refill()
    tb.totalReqs++
    
    if tb.tokens >= float64(n) {
        tb.tokens -= float64(n)
        tb.allowedReqs++
        return true
    }
    
    return false
}

func (tb *TokenBucketLimiter) Wait(ctx context.Context) error {
    return tb.WaitN(ctx, 1)
}

func (tb *TokenBucketLimiter) WaitN(ctx context.Context, n int) error {
    for {
        if tb.AllowN(n) {
            return nil
        }
        
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(time.Millisecond * 10):
            // 小睡眠以避免忙等待
        }
    }
}

func (tb *TokenBucketLimiter) Limit() int {
    return int(tb.refillRate)
}

func (tb *TokenBucketLimiter) Burst() int {
    return int(tb.capacity)
}

func (tb *TokenBucketLimiter) Reset() {
    tb.mu.Lock()
    defer tb.mu.Unlock()
    tb.tokens = tb.capacity
    tb.lastRefill = time.Now()
    tb.totalReqs = 0
    tb.allowedReqs = 0
}
```

## 提示3：滑动窗口算法
比固定窗口更精确，避免边界效应：

**关键洞察：**
- 在滑动时间窗口内跟踪最近请求的时间戳
- 每次请求前，移除超过窗口大小的老请求时间戳
- 如果剩余请求数小于速率限制，则允许请求

**相比固定窗口的优势：**
- 避免窗口边界处的突发流量
- 更准确的速率限制
- 流量随时间更平滑

```go
// 清理窗口外的旧请求
cutoff := now.Add(-windowSize)
requests = removeOlderThan(requests, cutoff)

// 检查是否在速率限制范围内
if len(requests) < rateLimit {
    requests = append(requests, now)
    return true  // 允许
}
```

## 提示4：固定窗口速率限制器
实现基于计数器的简单速率限制：
```go
type FixedWindowLimiter struct {
    mu          sync.Mutex
    rate        int
    windowSize  time.Duration
    count       int
    windowStart time.Time
    totalReqs   int64
    allowedReqs int64
}

func NewFixedWindowLimiter(rate int, windowSize time.Duration) RateLimiter {
    return &FixedWindowLimiter{
        rate:        rate,
        windowSize:  windowSize,
        windowStart: time.Now(),
    }
}

func (fw *FixedWindowLimiter) resetIfNeeded() {
    now := time.Now()
    if now.Sub(fw.windowStart) >= fw.windowSize {
        fw.count = 0
        fw.windowStart = now
    }
}

func (fw *FixedWindowLimiter) AllowN(n int) bool {
    fw.mu.Lock()
    defer fw.mu.Unlock()
    
    fw.resetIfNeeded()
    fw.totalReqs++
    
    if fw.count+n <= fw.rate {
        fw.count += n
        fw.allowedReqs++
        return true
    }
    
    return false
}

func (fw *FixedWindowLimiter) Wait(ctx context.Context) error {
    return fw.WaitN(ctx, 1)
}

func (fw *FixedWindowLimiter) WaitN(ctx context.Context, n int) error {
    for {
        if fw.AllowN(n) {
            return nil
        }
        
        // 计算到下一个窗口的时间
        fw.mu.Lock()
        nextWindow := fw.windowStart.Add(fw.windowSize)
        fw.mu.Unlock()
        
        waitTime := time.Until(nextWindow)
        if waitTime <= 0 {
            continue
        }
        
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(waitTime):
            // 窗口已重置，重新尝试
        }
    }
}
```

## 提示5：速率限制器工厂模式
创建灵活的工厂以支持不同类型的速率限制器：
```go
type RateLimiterConfig struct {
    Algorithm  string
    Rate       int
    Burst      int
    WindowSize time.Duration
}

type RateLimiterFactory struct{}

func NewRateLimiterFactory() *RateLimiterFactory {
    return &RateLimiterFactory{}
}

func (f *RateLimiterFactory) CreateLimiter(config RateLimiterConfig) (RateLimiter, error) {
    switch config.Algorithm {
    case "token_bucket":
        if config.Burst <= 0 {
            config.Burst = config.Rate
        }
        return NewTokenBucketLimiter(config.Rate, config.Burst), nil
        
    case "sliding_window":
        if config.WindowSize == 0 {
            config.WindowSize = time.Second
        }
        return NewSlidingWindowLimiter(config.Rate, config.WindowSize), nil
        
    case "fixed_window":
        if config.WindowSize == 0 {
            config.WindowSize = time.Second
        }
        return NewFixedWindowLimiter(config.Rate, config.WindowSize), nil
        
    default:
        return nil, fmt.Errorf("未知算法: %s", config.Algorithm)
    }
}
```

## 提示6：HTTP中间件实现
为HTTP处理器添加速率限制：
```go
func RateLimitMiddleware(limiter RateLimiter) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", limiter.Limit()))
                w.Header().Set("X-RateLimit-Remaining", "0")
                w.Header().Set("Retry-After", "1")
                http.Error(w, "速率限制已超出", http.StatusTooManyRequests)
                return
            }
            
            w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", limiter.Limit()))
            next.ServeHTTP(w, r)
        })
    }
}

// 基于IP的速率限制中间件
func PerIPRateLimitMiddleware(factory *RateLimiterFactory, config RateLimiterConfig) func(http.Handler) http.Handler {
    limiters := sync.Map{}
    
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ip := getClientIP(r)
            
            limiterInterface, _ := limiters.LoadOrStore(ip, func() RateLimiter {
                limiter, _ := factory.CreateLimiter(config)
                return limiter
            }())
            
            limiter := limiterInterface.(RateLimiter)
            
            if !limiter.Allow() {
                http.Error(w, "速率限制已超出", http.StatusTooManyRequests)
                return
            }
            
            next.ServeHTTP(w, r)
        })
    }
}

func getClientIP(r *http.Request) string {
    forwarded := r.Header.Get("X-Forwarded-For")
    if forwarded != "" {
        return strings.Split(forwarded, ",")[0]
    }
    return r.RemoteAddr
}
```

## 提示7：指标与监控
为速率限制器性能添加指标收集功能：
```go
type RateLimiterMetrics struct {
    TotalRequests   int64
    AllowedRequests int64
    DeniedRequests  int64
    AverageWaitTime time.Duration
    mu              sync.RWMutex
}

func (m *RateLimiterMetrics) RecordRequest(allowed bool, waitTime time.Duration) {
    m.mu.Lock()
    defer m.mu.Unlock()
    
    m.TotalRequests++
    if allowed {
        m.AllowedRequests++
    } else {
        m.DeniedRequests++
    }
    
    // 更新等待时间的移动平均值
    if m.TotalRequests == 1 {
        m.AverageWaitTime = waitTime
    } else {
        // 简单移动平均
        m.AverageWaitTime = time.Duration(
            (int64(m.AverageWaitTime)*9 + int64(waitTime)) / 10,
        )
    }
}

func (m *RateLimiterMetrics) GetStats() (total, allowed, denied int64, avgWait time.Duration) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return m.TotalRequests, m.AllowedRequests, m.DeniedRequests, m.AverageWaitTime
}

func (m *RateLimiterMetrics) SuccessRate() float64 {
    m.mu.RLock()
    defer m.mu.RUnlock()
    
    if m.TotalRequests == 0 {
        return 0.0
    }
    return float64(m.AllowedRequests) / float64(m.TotalRequests)
}

// 增强版速率限制器，带指标
type MetricsRateLimiter struct {
    limiter RateLimiter
    metrics *RateLimiterMetrics
}

func NewMetricsRateLimiter(limiter RateLimiter) *MetricsRateLimiter {
    return &MetricsRateLimiter{
        limiter: limiter,
        metrics: &RateLimiterMetrics{},
    }
}

func (m *MetricsRateLimiter) Allow() bool {
    start := time.Now()
    allowed := m.limiter.Allow()
    waitTime := time.Since(start)
    m.metrics.RecordRequest(allowed, waitTime)
    return allowed
}
```

## 速率限制核心概念：
- **令牌桶**：在保持平均速率的同时允许突发流量
- **滑动窗口**：精确的速率限制，无边界效应  
- **固定窗口**：简单高效，但在边界处允许突发流量
- **线程安全**：使用互斥锁处理并发访问
- **上下文取消**：在Wait方法中支持超时
- **HTTP集成**：为Web应用提供中间件，并设置正确的响应头
</rewritten_file>