# 挑战 28：支持多种淘汰策略的缓存实现

## 问题描述

在此挑战中，你将实现一个高性能、线程安全的缓存系统，支持多种淘汰策略。这是一个常见的面试题，用于测试你对数据结构、算法、并发编程和系统设计的理解。

你的任务是实现三种不同的缓存淘汰策略：

1. **LRU（最近最少使用）**：淘汰最近访问时间最久的项
2. **LFU（最不经常使用）**：淘汰访问次数最少的项
3. **FIFO（先进先出）**：淘汰最早加入的项，不考虑访问模式

每种实现都必须保证 get 和 put 操作的时间复杂度为 O(1)，并且必须是线程安全的。

## 要求

### 核心接口

所有缓存实现都必须满足以下接口：

```go
type Cache interface {
    // Get 根据键获取值。如果找到返回值和 true，否则返回 nil 和 false。
    Get(key string) (value interface{}, found bool)
    
    // Put 存储键值对。如果缓存已满，应根据其策略进行淘汰。
    Put(key string, value interface{})
    
    // Delete 删除键值对。如果键存在则返回 true，否则返回 false。
    Delete(key string) bool
    
    // Clear 清除缓存中的所有条目。
    Clear()
    
    // Size 返回当前缓存中的项目数量。
    Size() int
    
    // Capacity 返回缓存能容纳的最大项目数。
    Capacity() int
    
    // HitRate 返回缓存命中率，范围在 0 到 1 之间。
    HitRate() float64
}
```

### 性能要求

- **时间复杂度**：Get、Put 和 Delete 操作均为 O(1)
- **空间复杂度**：O(n)，其中 n 是缓存容量
- **线程安全**：所有操作必须支持并发安全使用
- **内存效率**：最小化内存开销并防止内存泄漏

### 实现要求

你必须实现：

1. **LRUCache**：使用双向链表 + 哈希表
2. **LFUCache**：使用频率追踪机制实现高效淘汰
3. **FIFOCache**：使用队列式淘汰机制
4. **ThreadSafeWrapper**：使任意缓存实现变为线程安全
5. **CacheFactory**：根据策略类型创建缓存实例

## 函数签名

### 1. LRU 缓存

```go
type LRUCache struct {
    // 私有字段 - 自行设计实现
}

// NewLRUCache 创建指定容量的新 LRU 缓存
func NewLRUCache(capacity int) *LRUCache

// 实现 Cache 接口方法
func (c *LRUCache) Get(key string) (interface{}, bool)
func (c *LRUCache) Put(key string, value interface{})
func (c *LRUCache) Delete(key string) bool
func (c *LRUCache) Clear()
func (c *LRUCache) Size() int
func (c *LRUCache) Capacity() int
func (c *LRUCache) HitRate() float64
```

### 2. LFU 缓存

```go
type LFUCache struct {
    // 私有字段 - 自行设计实现
}

// NewLFUCache 创建指定容量的新 LFU 缓存
func NewLFUCache(capacity int) *LFUCache

// 实现 Cache 接口方法
func (c *LFUCache) Get(key string) (interface{}, bool)
func (c *LFUCache) Put(key string, value interface{})
func (c *LFUCache) Delete(key string) bool
func (c *LFUCache) Clear()
func (c *LFUCache) Size() int
func (c *LFUCache) Capacity() int
func (c *LFUCache) HitRate() float64
```

### 3. FIFO 缓存

```go
type FIFOCache struct {
    // 私有字段 - 自行设计实现
}

// NewFIFOCache 创建指定容量的新 FIFO 缓存
func NewFIFOCache(capacity int) *FIFOCache

// 实现 Cache 接口方法
func (c *FIFOCache) Get(key string) (interface{}, bool)
func (c *FIFOCache) Put(key string, value interface{})
func (c *FIFOCache) Delete(key string) bool
func (c *FIFOCache) Clear()
func (c *FIFOCache) Size() int
func (c *FIFOCache) Capacity() int
func (c *FIFOCache) HitRate() float64
```

### 4. 线程安全包装器

```go
type ThreadSafeCache struct {
    // 私有字段 - 自行设计实现
}

// NewThreadSafeCache 包装任意缓存实现，使其线程安全
func NewThreadSafeCache(cache Cache) *ThreadSafeCache

// 使用适当锁实现 Cache 接口方法
func (c *ThreadSafeCache) Get(key string) (interface{}, bool)
func (c *ThreadSafeCache) Put(key string, value interface{})
func (c *ThreadSafeCache) Delete(key string) bool
func (c *ThreadSafeCache) Clear()
func (c *ThreadSafeCache) Size() int
func (c *ThreadSafeCache) Capacity() int
func (c *ThreadSafeCache) HitRate() float64
```

### 5. 缓存工厂

```go
type CachePolicy int

const (
    LRU CachePolicy = iota
    LFU
    FIFO
)

// NewCache 根据指定策略和容量创建缓存
func NewCache(policy CachePolicy, capacity int) Cache

// NewThreadSafeCacheWithPolicy 创建指定策略的线程安全缓存
func NewThreadSafeCacheWithPolicy(policy CachePolicy, capacity int) Cache
```

## 输入/输出示例

### LRU 缓存示例
```go
cache := NewLRUCache(2)

cache.Put("a", 1)
cache.Put("b", 2)
fmt.Println(cache.Get("a"))  // 输出: 1, true

cache.Put("c", 3)            // 淘汰 "b"（最近最少使用）
fmt.Println(cache.Get("b"))  // 输出: nil, false
fmt.Println(cache.Get("a"))  // 输出: 1, true
fmt.Println(cache.Get("c"))  // 输出: 3, true
```

### LFU 缓存示例
```go
cache := NewLFUCache(2)

cache.Put("a", 1)
cache.Put("b", 2)
cache.Get("a")               // "a" 的访问频率变为 2
cache.Get("a")               // "a" 的访问频率变为 3

cache.Put("c", 3)            // 淘汰 "b"（频率为 1，最低频）
fmt.Println(cache.Get("b"))  // 输出: nil, false
fmt.Println(cache.Get("a"))  // 输出: 1, true
fmt.Println(cache.Get("c"))  // 输出: 3, true
```

### FIFO 缓存示例
```go
cache := NewFIFOCache(2)

cache.Put("a", 1)
cache.Put("b", 2)
cache.Get("a")               // 不影响淘汰顺序

cache.Put("c", 3)            // 淘汰 "a"（先进先出）
fmt.Println(cache.Get("a"))  // 输出: nil, false
fmt.Println(cache.Get("b"))  // 输出: 2, true
fmt.Println(cache.Get("c"))  // 输出: 3, true
```

### 线程安全示例
```go
cache := NewThreadSafeCache(NewLRUCache(100))

// 安全地用于并发场景
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        for j := 0; j < 100; j++ {
            key := fmt.Sprintf("key-%d-%d", id, j)
            cache.Put(key, j)
            cache.Get(key)
        }
    }(i)
}
wg.Wait()

fmt.Printf("命中率: %.2f\n", cache.HitRate())
```

## 评估标准

### 正确性（40 分）
- 所有缓存策略正确运行
- 正确的淘汰行为
- 包装后具备线程安全性
- 正确处理边界情况

### 性能（25 分）
- 所有操作均为 O(1) 时间复杂度
- 内存使用高效
- 线程安全版本锁竞争最小

### 代码质量（20 分）
- 代码清晰、可读性强且结构良好
- 适当的抽象与接口设计
- 变量和函数命名恰当
- 注释合理

### 算法理解（15 分）
- 各淘汰策略的高效实现
- 对数据结构权衡的理解
- 并发访问模式的妥善处理

## 高级要求（加分项）

实现以下内容可获得额外分数：

1. **TTL 支持**：添加生存时间功能
2. **缓存指标**：详细统计信息（命中率、淘汰次数等）
3. **基准测试**：不同策略间的性能对比
4. **内存压力处理**：在内存压力下自动淘汰

## 约束条件

- 缓存容量至少为 1
- 键始终为非空字符串
- 值可以是任意 interface{} 类型
- 必须正确处理 nil 值
- 容量为 0 的缓存应始终未命中
- 线程安全操作应尽量减少锁的使用

## 提示

1. **LRU**：使用双向链表配合哈希表指向节点
2. **LFU**：考虑使用频率桶或最小堆来高效选择淘汰项
3. **FIFO**：简单的队列或环形缓冲区即可
4. **线程安全**：使用 sync.RWMutex 以提升读操作性能
5. **内存管理**：移除节点时注意避免内存泄漏
6. **测试**：测试容量为 1、并发访问和大数据集等边界情况

## 时间限制

此挑战应在 60-90 分钟内完成，适用于面试场景。

## 学习资源

参见 [learning.md](learning.md) 文件，了解缓存实现模式、算法及最佳实践的完整信息。

## 成功标准

成功的实现应满足：
- 通过所有提供的测试用例
- 展示基本操作的 O(1) 性能
- 安全处理并发访问
- 展现对不同淘汰策略的理解
- 包含适当的错误处理和边界情况管理