# 缓存实现学习资料

## 缓存简介

缓存是计算机科学中一种基础技术，用于将频繁访问的数据存储在快速访问的位置。良好的缓存实现可以通过减少从较慢存储系统访问数据所需的时间，显著提升应用程序性能。

### 为什么缓存很重要

1. **性能**：通过将频繁访问的数据存储在靠近应用程序的位置来降低延迟
2. **资源效率**：减轻数据库等后端系统的负载
3. **可扩展性**：帮助应用程序在相同资源下处理更多请求
4. **成本降低**：最小化昂贵操作，如数据库查询或API调用

### 缓存基础

缓存本质上是一个容量有限的键值存储。当缓存达到其容量时，必须决定哪些项目需要移除以腾出空间给新项目。这一决策由**淘汰策略**做出。

## 缓存淘汰策略

### 1. LRU（最近最少使用）

LRU 淘汰最近访问（读取或写入）次数最少的项目。

**算法**：
- 维护一个按访问时间排序的双向链表
- 使用哈希表实现 O(1) 的键查找
- 访问时：将项目移动到链表前端
- 淘汰时：从链表尾部移除项目

**时间复杂度**：所有操作均为 O(1)
**空间复杂度**：O(n)，其中 n 为缓存容量

```go
// LRU 缓存实现概念
type LRUCache struct {
    capacity int
    cache    map[string]*Node
    head     *Node  // 最近使用的
    tail     *Node  // 最久未使用的
}

type Node struct {
    key   string
    value interface{}
    prev  *Node
    next  *Node
}
```

**适用场景**：
- 操作系统页面替换
- CPU 缓存管理
- 网络浏览器缓存
- 数据库缓冲池

**优点**：
- 对时间局部性表现良好
- 淘汰策略直观
- 适用于大多数通用场景

**缺点**：
- 不考虑访问频率
- 可能受顺序扫描影响而破坏缓存局部性

### 2. LFU（最不经常使用）

LFU 淘汰被访问次数最少的项目。

**算法**：
- 为每个项目维护一个频率计数器
- 使用最小堆或频率桶实现高效的淘汰
- 访问时：增加频率计数器
- 淘汰时：移除频率最低的项目

**时间复杂度**：正确实现下 get/put 为 O(1)
**空间复杂度**：O(n)

```go
// LFU 缓存实现概念
type LFUCache struct {
    capacity   int
    minFreq    int
    cache      map[string]*Node
    freqGroups map[int]*FreqGroup  // 频率 -> 节点列表
}

type FreqGroup struct {
    freq int
    head *Node
    tail *Node
}
```

**适用场景**：
- 具有稳定访问模式的长期运行应用
- 科学计算中重复访问数据
- CDN 系统

**优点**：
- 适用于具有明显热点数据的工作负载
- 能很好地适应随时间变化的访问模式
- 在某些数据访问频率远高于其他数据的场景中表现优异

**缺点**：
- 实现更复杂
- 新项目在缓存满时可能立即被淘汰
- 频率计数可能随时间变得过时

### 3. FIFO（先进先出）

FIFO 淘汰缓存中最旧的项目，与访问模式无关。

**算法**：
- 使用队列或链表维护插入顺序
- 插入时：添加到前端
- 淘汰时：从后端移除

**时间复杂度**：所有操作均为 O(1)
**空间复杂度**：O(n)

```go
// FIFO 缓存实现概念
type FIFOCache struct {
    capacity int
    cache    map[string]*Node
    head     *Node  // 最新的项目
    tail     *Node  // 最旧的项目
}
```

**适用场景**：
- 简单的缓存场景
- 当访问模式未知时
- 内存受限的嵌入式系统

**优点**：
- 实现和理解简单
- 行为可预测
- 无需跟踪访问模式

**缺点**：
- 完全忽略访问模式
- 可能淘汰频繁使用的项目
- 通常缓存命中率较低

## 高级缓存概念

### 线程安全

真实世界的缓存必须处理并发访问：

```go
type ThreadSafeCache struct {
    mu    sync.RWMutex
    cache Cache
}

func (c *ThreadSafeCache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.cache.Get(key)
}

func (c *ThreadSafeCache) Put(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.cache.Put(key, value)
}
```

### 缓存指标

需要跟踪的重要指标：

1. **命中率**：从缓存中服务的请求数百分比
2. **未命中率**：不在缓存中的请求数百分比
3. **淘汰数量**：被淘汰项目的数量
4. **平均响应时间**：性能测量

```go
type CacheMetrics struct {
    hits      int64
    misses    int64
    evictions int64
}

func (m *CacheMetrics) HitRate() float64 {
    total := m.hits + m.misses
    if total == 0 {
        return 0
    }
    return float64(m.hits) / float64(total)
}
```

### TTL（生存时间）

项目可以在一定时间后自动过期：

```go
type CacheEntry struct {
    value     interface{}
    timestamp time.Time
    ttl       time.Duration
}

func (e *CacheEntry) IsExpired() bool {
    if e.ttl == 0 {
        return false
    }
    return time.Since(e.timestamp) > e.ttl
}
```

## 实现策略

### 内存管理

```go
// 正确清理以防止内存泄漏
func (c *Cache) evict(node *Node) {
    // 从哈希表中删除
    delete(c.cache, node.key)
    
    // 从链表中删除
    c.removeFromList(node)
    
    // 清除引用以帮助垃圾回收
    node.prev = nil
    node.next = nil
    node.value = nil
}
```

### 接口设计

设计灵活且易于测试：

```go
type Cache interface {
    Get(key string) (value interface{}, found bool)
    Put(key string, value interface{})
    Delete(key string) bool
    Clear()
    Size() int
    Capacity() int
}

type EvictionPolicy interface {
    OnAccess(key string)
    OnInsert(key string)
    OnDelete(key string)
    SelectVictim() string
}
```

## 性能优化

### 内存布局

```go
// 使用数组结构以提高缓存局部性
type OptimizedLRU struct {
    keys     []string
    values   []interface{}
    prev     []int
    next     []int
    keyIndex map[string]int
    head     int
    tail     int
    size     int
    capacity int
}
```

### 避免分配

```go
// 预分配节点池以减少垃圾回收压力
type NodePool struct {
    nodes []Node
    free  []int
}

func (p *NodePool) Get() *Node {
    if len(p.free) == 0 {
        return &Node{}
    }
    idx := p.free[len(p.free)-1]
    p.free = p.free[:len(p.free)-1]
    return &p.nodes[idx]
}
```

## 测试策略

### 单元测试

```go
func TestCacheEviction(t *testing.T) {
    cache := NewLRUCache(2)
    
    // 填充缓存
    cache.Put("a", 1)
    cache.Put("b", 2)
    
    // 触发淘汰
    cache.Put("c", 3)
    
    // 验证最旧的项目已被淘汰
    _, found := cache.Get("a")
    assert.False(t, found)
}
```

### 并发测试

```go
func TestConcurrentAccess(t *testing.T) {
    cache := NewThreadSafeCache(100)
    
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for j := 0; j < 1000; j++ {
                key := fmt.Sprintf("key-%d-%d", id, j)
                cache.Put(key, j)
                cache.Get(key)
            }
        }(i)
    }
    wg.Wait()
}
```

### 基准测试

```go
func BenchmarkCacheGet(b *testing.B) {
    cache := NewLRUCache(1000)
    
    // 填充缓存
    for i := 0; i < 1000; i++ {
        cache.Put(fmt.Sprintf("key-%d", i), i)
    }
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        cache.Get(fmt.Sprintf("key-%d", i%1000))
    }
}
```

## 实际应用考虑

### 缓存雪崩预防

```go
type SafeCache struct {
    cache  Cache
    groups singleflight.Group
}

func (c *SafeCache) GetOrCompute(key string, compute func() interface{}) interface{} {
    if value, found := c.cache.Get(key); found {
        return value
    }
    
    // 防止缓存雪崩
    value, _, _ := c.groups.Do(key, func() (interface{}, error) {
        if value, found := c.cache.Get(key); found {
            return value, nil
        }
        
        computed := compute()
        c.cache.Put(key, computed)
        return computed, nil
    })
    
    return value
}
```

### 分布式缓存

```go
type DistributedCache interface {
    Get(key string) (interface{}, bool)
    Put(key string, value interface{})
    Invalidate(key string)
    InvalidatePattern(pattern string)
}
```

### 内存压力处理

```go
func (c *Cache) handleMemoryPressure() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    
    if m.Alloc > c.maxMemory {
        // 积极淘汰项目
        evictCount := c.size / 4
        for i := 0; i < evictCount; i++ {
            c.evictLRU()
        }
    }
}
```

## 缓存策略对比

| 策略 | 获取时间 | 插入时间 | 空间 | 最佳应用场景 |
|--------|----------|----------|--------|---------------|
| LRU    | O(1)     | O(1)     | O(n)   | 通用场景，时间局部性 |
| LFU    | O(1)     | O(1)     | O(n)   | 稳定访问模式，热点数据 |
| FIFO   | O(1)     | O(1)     | O(n)   | 简单场景，未知模式 |

## 进一步阅读

1. [缓存替换策略](https://zh.wikipedia.org/wiki/缓存替换策略)
2. [LFU-DA 缓存算法](https://www.usenix.org/legacy/publications/library/proceedings/usits97/full_papers/arlitt/arlitt.pdf)
3. [使用 Redis 扩展缓存](https://redis.io/topics/lru-cache)
4. [Linux 内核页缓存](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
5. [Caffeine：高性能 Java 缓存库](https://github.com/ben-manes/caffeine)