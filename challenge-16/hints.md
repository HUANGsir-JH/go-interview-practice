# 第16关提示：使用基准测试进行性能优化

## 提示1：理解Go基准测试
首先设置适当的基准测试来衡量性能：
```go
import "testing"

func BenchmarkSlowSort(b *testing.B) {
    data := make([]int, 1000)
    for i := range data {
        data[i] = rand.Intn(1000)
    }
    
    b.ResetTimer() // 设置完成后重置计时器
    
    for i := 0; i < b.N; i++ {
        // 每次迭代都创建副本以确保状态一致
        testData := make([]int, len(data))
        copy(testData, data)
        SlowSort(testData)
    }
}

func BenchmarkOptimizedSort(b *testing.B) {
    data := make([]int, 1000)
    for i := range data {
        data[i] = rand.Intn(1000)
    }
    
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        testData := make([]int, len(data))
        copy(testData, data)
        OptimizedSort(testData)
    }
}
```

## 提示2：优化SlowSort - 算法改进
用Go内置的排序替换低效的排序算法：
```go
import "sort"

// 不再实现冒泡排序或选择排序
func OptimizedSort(data []int) {
    // 使用Go高度优化的排序算法
    sort.Ints(data)
}

// 如果需要自定义比较
func OptimizedSortCustom(data []interface{}, less func(i, j int) bool) {
    sort.Slice(data, less)
}
```

## 提示3：字符串构建优化 - 减少内存分配
使用 strings.Builder 避免重复的字符串拼接：
```go
import "strings"

// 之前：低效的字符串拼接
func InefficientStringBuilder(words []string) string {
    result := ""
    for _, word := range words {
        result += word + " " // 每次都创建新字符串
    }
    return result
}

// 之后：使用 strings.Builder
func OptimizedStringBuilder(words []string) string {
    var builder strings.Builder
    
    // 如果知道大致大小，可预先分配容量
    totalLen := 0
    for _, word := range words {
        totalLen += len(word) + 1
    }
    builder.Grow(totalLen)
    
    for i, word := range words {
        builder.WriteString(word)
        if i < len(words)-1 {
            builder.WriteByte(' ')
        }
    }
    return builder.String()
}
```

## 提示4：昂贵计算 - 记忆化和缓存
使用记忆化避免重复计算：
```go
import "sync"

type MemoizedCalculator struct {
    cache map[int]int
    mutex sync.RWMutex
}

func NewMemoizedCalculator() *MemoizedCalculator {
    return &MemoizedCalculator{
        cache: make(map[int]int),
    }
}

func (mc *MemoizedCalculator) ExpensiveCalculation(n int) int {
    // 先检查缓存
    mc.mutex.RLock()
    if result, exists := mc.cache[n]; exists {
        mc.mutex.RUnlock()
        return result
    }
    mc.mutex.RUnlock()
    
    // 执行计算
    result := performActualCalculation(n)
    
    // 存入缓存
    mc.mutex.Lock()
    mc.cache[n] = result
    mc.mutex.Unlock()
    
    return result
}

// 对于简单情况，可以使用 sync.Map 实现并发访问
var calculationCache sync.Map

func OptimizedExpensiveCalculation(n int) int {
    if cached, found := calculationCache.Load(n); found {
        return cached.(int)
    }
    
    result := performActualCalculation(n)
    calculationCache.Store(n, result)
    return result
}
```

## 提示5：高内存分配搜索 - 内存池与高效数据结构
通过复用内存和使用合适的数据结构减少内存分配：
```go
import "sync"

// 用于复用切片的内存池
var searchResultPool = sync.Pool{
    New: func() interface{} {
        return make([]int, 0, 100) // 预先分配容量
    },
}

func OptimizedSearch(data []int, target int) []int {
    // 从池中获取切片
    results := searchResultPool.Get().([]int)
    results = results[:0] // 重置长度但保留容量
    
    defer func() {
        // 返回池中供复用
        searchResultPool.Put(results)
    }()
    
    for i, val := range data {
        if val == target {
            results = append(results, i)
        }
    }
    
    // 由于要将切片归还池中，需返回副本
    finalResults := make([]int, len(results))
    copy(finalResults, results)
    return finalResults
}

// 替代方案：如果需要反复查找，可使用 map 实现更快查询
func OptimizedSearchWithIndex(data []int) map[int][]int {
    index := make(map[int][]int)
    for i, val := range data {
        index[val] = append(index[val], i)
    }
    return index
}
```

## 提示6：分析与测量
使用Go的分析工具识别性能瓶颈：
```go
import (
    "runtime/pprof"
    "os"
)

func BenchmarkWithMemoryProfile(b *testing.B) {
    // 启用内存分析
    f, err := os.Create("mem.prof")
    if err != nil {
        b.Fatal(err)
    }
    defer f.Close()
    
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        // 在此处调用你的函数
        OptimizedFunction()
    }
    
    pprof.WriteHeapProfile(f)
}

// 运行基准测试并查看内存分配统计
// go test -bench=. -benchmem
func BenchmarkMemoryUsage(b *testing.B) {
    b.ReportAllocs() // 报告内存分配统计信息
    
    for i := 0; i < b.N; i++ {
        result := YourFunction()
        _ = result // 防止编译器优化
    }
}
```

## 提示7：避免常见性能陷阱
实现高效模式并避免常见错误：
```go
// 避免：创建不必要的切片
func InefficientProcessing(data []string) []string {
    var results []string
    for _, item := range data {
        if len(item) > 5 {
            results = append(results, strings.ToUpper(item))
        }
    }
    return results
}

// 更好：预分配并尽可能原地处理
func EfficientProcessing(data []string) []string {
    // 根据估计大小预分配
    results := make([]string, 0, len(data)/2)
    
    for _, item := range data {
        if len(item) > 5 {
            results = append(results, strings.ToUpper(item))
        }
    }
    return results
}

// 对某些场景更优：无需分配新切片即可处理
func ProcessInPlace(data []string, callback func(string)) {
    for _, item := range data {
        if len(item) > 5 {
            callback(strings.ToUpper(item))
        }
    }
}
```

## 提示8：对不同输入规模进行基准测试
使用不同输入规模测试算法复杂度：
```go
func BenchmarkSortSmall(b *testing.B)  { benchmarkSort(b, 100) }
func BenchmarkSortMedium(b *testing.B) { benchmarkSort(b, 1000) }
func BenchmarkSortLarge(b *testing.B)  { benchmarkSort(b, 10000) }

func benchmarkSort(b *testing.B, size int) {
    data := make([]int, size)
    for i := range data {
        data[i] = rand.Intn(size)
    }
    
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        testData := make([]int, len(data))
        copy(testData, data)
        OptimizedSort(testData)
    }
}
```

## 关键性能优化技术：
- **算法选择**：使用高效算法（O(n log n) 优于 O(n²)）
- **内存分配**：最小化分配，复用内存池
- **字符串操作**：拼接时使用 strings.Builder
- **缓存**：为昂贵计算实现记忆化
- **数据结构**：选择合适的数据结构（map 与 slice 的权衡）
- **分析**：使用基准测试和分析工具衡量优化效果
- **预分配**：对已知容量的切片/映射进行预分配