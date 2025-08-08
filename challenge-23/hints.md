# 挑战 23：字符串模式匹配提示

## 提示 1：朴素模式匹配 - 暴力法
从最简单的逐位置检查方法开始：
```go
func NaivePatternMatch(text, pattern string) []int {
    var matches []int
    
    if len(pattern) == 0 || len(pattern) > len(text) {
        return matches
    }
    
    for i := 0; i <= len(text)-len(pattern); i++ {
        match := true
        for j := 0; j < len(pattern); j++ {
            if text[i+j] != pattern[j] {
                match = false
                break
            }
        }
        if match {
            matches = append(matches, i)
        }
    }
    
    return matches
}
```

## 提示 2：KMP 算法 - 模式预处理
首先，为模式构建前缀函数（失败函数）：
```go
func computeLPS(pattern string) []int {
    m := len(pattern)
    lps := make([]int, m)
    length := 0
    i := 1
    
    for i < m {
        if pattern[i] == pattern[length] {
            length++
            lps[i] = length
            i++
        } else {
            if length != 0 {
                length = lps[length-1]
            } else {
                lps[i] = 0
                i++
            }
        }
    }
    return lps
}
```

## 提示 3：KMP 算法 - 主搜索函数
使用 LPS 数组避免不必要的字符比较：
```go
func KMPSearch(text, pattern string) []int {
    var matches []int
    
    if len(pattern) == 0 || len(pattern) > len(text) {
        return matches
    }
    
    lps := computeLPS(pattern)
    i := 0 // 文本索引
    j := 0 // 模式索引
    
    for i < len(text) {
        if pattern[j] == text[i] {
            i++
            j++
        }
        
        if j == len(pattern) {
            matches = append(matches, i-j)
            j = lps[j-1]
        } else if i < len(text) && pattern[j] != text[i] {
            if j != 0 {
                j = lps[j-1]
            } else {
                i++
            }
        }
    }
    
    return matches
}
```

## 提示 4：Rabin-Karp 算法 - 哈希函数设置
使用滚动哈希高效比较模式与文本窗口：
```go
const (
    prime = 101 // 用于哈希的质数
    base  = 256 // ASCII 字符数量
)

func RabinKarpSearch(text, pattern string) []int {
    var matches []int
    
    if len(pattern) == 0 || len(pattern) > len(text) {
        return matches
    }
    
    m := len(pattern)
    n := len(text)
    
    // 计算哈希值
    patternHash := 0
    textHash := 0
    h := 1
    
    // h = base^(m-1) % prime
    for i := 0; i < m-1; i++ {
        h = (h * base) % prime
    }
    
    // 计算初始哈希值
    for i := 0; i < m; i++ {
        patternHash = (base*patternHash + int(pattern[i])) % prime
        textHash = (base*textHash + int(text[i])) % prime
    }
    
    // 其余实现...
}
```

## 提示 5：Rabin-Karp 算法 - 滚动哈希实现
实现滚动哈希技术以高效滑动窗口：
```go
func RabinKarpSearch(text, pattern string) []int {
    var matches []int
    
    if len(pattern) == 0 || len(pattern) > len(text) {
        return matches
    }
    
    m := len(pattern)
    n := len(text)
    
    patternHash := 0
    textHash := 0
    h := 1
    
    // 计算 h = base^(m-1) % prime
    for i := 0; i < m-1; i++ {
        h = (h * base) % prime
    }
    
    // 计算初始哈希值
    for i := 0; i < m; i++ {
        patternHash = (base*patternHash + int(pattern[i])) % prime
        textHash = (base*textHash + int(text[i])) % prime
    }
    
    // 逐个滑动模式在文本上的窗口
    for i := 0; i <= n-m; i++ {
        // 检查哈希值是否匹配
        if patternHash == textHash {
            // 逐字符检查以避免误报
            match := true
            for j := 0; j < m; j++ {
                if text[i+j] != pattern[j] {
                    match = false
                    break
                }
            }
            if match {
                matches = append(matches, i)
            }
        }
        
        // 计算下一个窗口的哈希值
        if i < n-m {
            textHash = (base*(textHash-int(text[i])*h) + int(text[i+m])) % prime
            
            // 处理负哈希值
            if textHash < 0 {
                textHash = textHash + prime
            }
        }
    }
    
    return matches
}
```

## 提示 6：边界情况和输入验证
在所有算法中正确处理边界情况：
```go
func handleEdgeCases(text, pattern string) ([]int, bool) {
    // 空模式
    if len(pattern) == 0 {
        return []int{}, true
    }
    
    // 模式长度超过文本
    if len(pattern) > len(text) {
        return []int{}, true
    }
    
    // 空文本但非空模式
    if len(text) == 0 {
        return []int{}, true
    }
    
    // 继续正常处理
    return nil, false
}
```

## 提示 7：算法优化技巧
考虑以下优化以提升性能：
```go
// 对于 KMP：优化 LPS 计算
func computeLPSOptimized(pattern string) []int {
    m := len(pattern)
    lps := make([]int, m)
    
    for i, length := 1, 0; i < m; {
        if pattern[i] == pattern[length] {
            length++
            lps[i] = length
            i++
        } else if length != 0 {
            length = lps[length-1]
        } else {
            lps[i] = 0
            i++
        }
    }
    return lps
}

// 对于 Rabin-Karp：使用更好的哈希函数减少冲突
func betterHash(s string) uint64 {
    var hash uint64 = 0
    for i := 0; i < len(s); i++ {
        hash = hash*31 + uint64(s[i])
    }
    return hash
}
```

## 提示 8：性能对比与测试
创建基准测试以比较算法性能：
```go
import "testing"

func BenchmarkNaive(b *testing.B) {
    text := strings.Repeat("ABCDEFGH", 1000)
    pattern := "DEFG"
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        NaivePatternMatch(text, pattern)
    }
}

func BenchmarkKMP(b *testing.B) {
    text := strings.Repeat("ABCDEFGH", 1000)
    pattern := "DEFG"
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        KMPSearch(text, pattern)
    }
}
```

## 关键模式匹配概念：
- **朴素方法**：简单但时间复杂度为 O(n*m)
- **KMP 算法**：利用前缀函数避免重复比较
- **滚动哈希**：Rabin-Karp 使用哈希值进行快速比较
- **LPS 数组**：最长真前缀同时也是后缀
- **哈希冲突**：Rabin-Karp 需要逐字符验证
- **边界情况**：妥善处理空字符串和边界条件
- **时间复杂度**：理解每种算法的最佳适用场景