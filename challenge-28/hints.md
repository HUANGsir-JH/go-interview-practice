# 挑战28提示：支持多种淘汰策略的缓存实现

## 提示1：LRU缓存设计模式
LRU（最近最少使用）要求访问和淘汰操作均为O(1)：

**数据结构选择：**
- **哈希表**：通过键实现O(1)的缓存节点访问
- **双向链表**：在任意位置实现O(1)的插入/删除
- **虚拟头尾节点**：简化链表操作中的边界情况

**核心组件：**
- 包含`prev`/`next`指针的节点结构
- 用于快速查找的映射：`map[string]*Node`
- 虚拟节点避免空指针检查

```go
type LRUNode struct {
    key, value interface{}
    prev, next *LRUNode
}

// 始终在头节点后插入，从尾节点前移除
head.next = cache.tail  // 初始化空列表
tail.prev = cache.head
```

## 提示2：LRU操作逻辑
理解核心LRU操作：

**Get操作：**
- 若键存在：将节点移至头部（标记为最近使用），返回值
- 若键不存在：返回缓存未命中

**Put操作：**
- 若键存在：更新值，并移至头部
- 若键不存在：创建新节点，插入头部
- 若已达容量：先移除尾部节点（最久未使用），再添加新节点

**关键辅助方法：**
```go
func moveToHead(node) {
    removeNode(node)  // 从当前位置解绑
    addToHead(node)   // 插入到虚拟头节点之后
}

func addToHead(node) {
    node.next = head.next
    node.prev = head
    head.next.prev = node
    head.next = node
}

func removeTail() {
    lru := tail.prev  // 获取最久未使用的节点
    removeNode(lru)   // 解绑该节点
    return lru
}
```

## 提示3：LFU缓存设计
LFU（最不经常使用）需要跟踪访问频率：

**核心概念：** 将节点按频率分组存储于独立的双向链表中
- `freqMap[1]` → 访问次数为1的节点列表
- `freqMap[2]` → 访问次数为2的节点列表  
- 维护`minFreq`以确定应从哪个频率列表中淘汰

**数据结构：**
- 节点包含`freq`字段记录访问次数
- `freqMap`将频率映射到节点列表的虚拟头节点
- 频率增加时，将节点移动到新的频率列表

```go
type LFUNode struct {
    key, value interface{}
    freq       int
    prev, next *LFUNode
}

// 将节点从频率N移动到频率N+1
func updateFreq(node) {
    removeFromFreqList(node, oldFreq)
    node.freq++
    addToFreqList(node, newFreq)
}
```
```

## 提示4：LFU缓存 - Get与Put实现
处理频率更新与淘汰：
```go
func (c *LFUCache) Get(key string) (interface{}, bool) {
    if node, exists := c.cache[key]; exists {
        c.updateFreq(node)
        c.hits++
        return node.value, true
    }
    c.misses++
    return nil, false
}

func (c *LFUCache) updateFreq(node *LFUNode) {
    oldFreq := node.freq
    newFreq := oldFreq + 1
    
    c.removeFromFreqList(node)
    node.freq = newFreq
    c.addToFreqList(node, newFreq)
    
    // 必要时更新 minFreq
    if oldFreq == c.minFreq && c.isFreqListEmpty(oldFreq) {
        c.minFreq++
    }
}

func (c *LFUCache) isFreqListEmpty(freq int) bool {
    head := c.freqMap[freq]
    return head != nil && head.next == head
}

func (c *LFUCache) Put(key string, value interface{}) {
    if c.capacity == 0 {
        return
    }
    
    if node, exists := c.cache[key]; exists {
        node.value = value
        c.updateFreq(node)
        return
    }
    
    if c.size >= c.capacity {
        c.evict()
    }
    
    newNode := &LFUNode{key: key, value: value, freq: 1}
    c.cache[key] = newNode
    c.addToFreqList(newNode, 1)
    c.minFreq = 1
    c.size++
}

func (c *LFUCache) evict() {
    head := c.getFreqList(c.minFreq)
    victim := head.prev
    c.removeFromFreqList(victim)
    delete(c.cache, victim.key)
    c.size--
}
```

## 提示5：FIFO缓存 - 简单队列结构
使用切片实现FIFO队列：
```go
type FIFOCache struct {
    capacity int
    cache    map[string]interface{}
    order    []string
    hits     int64
    misses   int64
}

func NewFIFOCache(capacity int) *FIFOCache {
    return &FIFOCache{
        capacity: capacity,
        cache:    make(map[string]interface{}),
        order:    make([]string, 0, capacity),
    }
}

func (c *FIFOCache) Get(key string) (interface{}, bool) {
    if value, exists := c.cache[key]; exists {
        c.hits++
        return value, true
    }
    c.misses++
    return nil, false
}

func (c *FIFOCache) Put(key string, value interface{}) {
    if _, exists := c.cache[key]; exists {
        c.cache[key] = value
        return
    }
    
    if len(c.cache) >= c.capacity {
        // 移除最早进入的（队首）
        oldest := c.order[0]
        delete(c.cache, oldest)
        c.order = c.order[1:]
    }
    
    c.cache[key] = value
    c.order = append(c.order, key)
}

func (c *FIFOCache) Delete(key string) bool {
    if _, exists := c.cache[key]; exists {
        delete(c.cache, key)
        
        // 从顺序切片中移除
        for i, k := range c.order {
            if k == key {
                c.order = append(c.order[:i], c.order[i+1:]...)
                break
            }
        }
        return true
    }
    return false
}
```

## 提示6：线程安全包装器
使用读写互斥锁实现线程安全：
```go
import "sync"

type ThreadSafeCache struct {
    cache Cache
    mutex sync.RWMutex
}

func NewThreadSafeCache(cache Cache) *ThreadSafeCache {
    return &ThreadSafeCache{
        cache: cache,
    }
}

func (c *ThreadSafeCache) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.cache.Get(key)
}

func (c *ThreadSafeCache) Put(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.cache.Put(key, value)
}

func (c *ThreadSafeCache) Delete(key string) bool {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    return c.cache.Delete(key)
}

func (c *ThreadSafeCache) Clear() {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.cache.Clear()
}

func (c *ThreadSafeCache) Size() int {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.cache.Size()
}

func (c *ThreadSafeCache) Capacity() int {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.cache.Capacity()
}

func (c *ThreadSafeCache) HitRate() float64 {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.cache.HitRate()
}
```

## 提示7：缓存工厂模式
实现工厂模式用于缓存创建：
```go
type CachePolicy int

const (
    LRU CachePolicy = iota
    LFU
    FIFO
)

func NewCache(policy CachePolicy, capacity int) Cache {
    switch policy {
    case LRU:
        return NewLRUCache(capacity)
    case LFU:
        return NewLFUCache(capacity)
    case FIFO:
        return NewFIFOCache(capacity)
    default:
        return NewLRUCache(capacity)
    }
}

func NewThreadSafeCacheWithPolicy(policy CachePolicy, capacity int) Cache {
    baseCache := NewCache(policy, capacity)
    return NewThreadSafeCache(baseCache)
}

// 测试用工具函数
func BenchmarkCache(cache Cache, operations int) {
    start := time.Now()
    
    for i := 0; i < operations; i++ {
        key := fmt.Sprintf("key_%d", i%1000)
        
        if i%3 == 0 {
            cache.Put(key, i)
        } else {
            cache.Get(key)
        }
    }
    
    duration := time.Since(start)
    fmt.Printf("完成 %d 次操作耗时 %v\n", operations, duration)
    fmt.Printf("命中率: %.2f%%\n", cache.HitRate()*100)
}
```

## 缓存实现核心概念：
- **O(1)操作**：使用哈希表实现常数时间访问
- **双向链表**：高效支持LRU的插入与删除
- **频率桶**：按频率分组节点以支持LFU
- **线程安全**：使用RWMutex处理并发访问
- **内存管理**：正确清理防止内存泄漏
- **工厂模式**：灵活的缓存创建与配置