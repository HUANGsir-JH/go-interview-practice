# 字符串模式匹配学习资料

## 字符串模式匹配简介

字符串模式匹配是指在较长的文本字符串中查找模式字符串出现的位置。这一基础算法广泛应用于以下场景：

- 文本编辑器（查找和替换）
- 生物信息学（DNA序列匹配）
- 互联网搜索引擎
- 数据挖掘与分析
- 垃圾邮件过滤器和安全系统

在本学习材料中，我们将探讨三种不同的字符串模式匹配算法：

1. 暴力（朴素）算法
2. 克努斯-莫里斯-普拉特（KMP）算法
3. 拉宾-卡普（Rabin-Karp）算法

## 1. 暴力模式匹配算法

暴力方法是字符串匹配最直接的方式。它从文本中的每个可能位置开始检查是否匹配。

### 暴力算法的工作原理

1. 将模式对齐到文本开头
2. 逐个比较模式与文本对应位置的字符
3. 如果所有字符都匹配，则记录起始位置
4. 将模式向右移动一个位置
5. 重复步骤2-4，直到到达文本末尾

### 在Go语言中实现暴力算法

```go
func NaivePatternMatch(text, pattern string) []int {
    matches := []int{}
    
    // 处理边界情况
    if len(pattern) == 0 || len(text) < len(pattern) {
        return matches
    }
    
    // 检查文本中每个可能的位置
    for i := 0; i <= len(text)-len(pattern); i++ {
        j := 0
        
        // 检查该位置是否匹配
        for j < len(pattern) && text[i+j] == pattern[j] {
            j++
        }
        
        // 如果j达到模式末尾，说明找到匹配
        if j == len(pattern) {
            matches = append(matches, i)
        }
    }
    
    return matches
}
```

### 暴力算法的时间复杂度

- **时间复杂度**：O(n×m)，其中n是文本长度，m是模式长度
- **空间复杂度**：O(k)，其中k是找到的匹配数量

暴力算法实现简单，但对于大文本或存在大量部分匹配的情况效率较低。

## 2. 克努斯-莫里斯-普拉特（KMP）算法

KMP算法通过避免失配时的重复比较来改进暴力方法。它使用预处理表（称为“失败函数”或“最长真前缀也是后缀”数组）来跳过已知会匹配的字符。

### KMP算法的工作原理

1. 预处理模式以构建部分匹配表（也称“LPS”或“π”表）
2. 利用此表确定失配时应将模式移多少位
3. 不回溯文本——文本中的每个字符仅被检查一次

### 构建LPS（最长前缀后缀）数组

LPS数组帮助确定模式在每个位置上最长的真前缀同时也是后缀的部分。这些信息用于避免重复比较。

```go
func computeLPSArray(pattern string) []int {
    m := len(pattern)
    lps := make([]int, m)
    
    // 上一个最长前后缀的长度
    length := 0
    i := 1
    
    // 循环计算lps[i]，i从1到m-1
    for i < m {
        if pattern[i] == pattern[length] {
            length++
            lps[i] = length
            i++
        } else {
            // 这是关键部分
            if length != 0 {
                length = lps[length-1]
                // 注意：这里不增加i
            } else {
                lps[i] = 0
                i++
            }
        }
    }
    
    return lps
}
```

### 在Go语言中实现KMP算法

```go
func KMPSearch(text, pattern string) []int {
    matches := []int{}
    
    // 处理边界情况
    if len(pattern) == 0 || len(text) < len(pattern) {
        return matches
    }
    
    n := len(text)
    m := len(pattern)
    
    // 预处理模式
    lps := computeLPSArray(pattern)
    
    i := 0 // 文本索引
    j := 0 // 模式索引
    
    for i < n {
        // 当前字符匹配，两个指针都向前移动
        if pattern[j] == text[i] {
            i++
            j++
        }
        
        // 找到完整匹配
        if j == m {
            matches = append(matches, i-j)
            // 使用lps调整模式位置进行下一次匹配
            j = lps[j-1]
        } else if i < n && pattern[j] != text[i] {
            // 匹配j个字符后发生失配
            if j != 0 {
                // 使用lps调整模式位置
                j = lps[j-1]
            } else {
                // 未找到匹配，移动到文本下一个字符
                i++
            }
        }
    }
    
    return matches
}
```

### KMP算法的时间复杂度

- **时间复杂度**：O(n+m)，其中n是文本长度，m是模式长度
- **空间复杂度**：O(m)用于LPS数组，加上O(k)用于存储匹配结果

KMP算法比暴力方法高效得多，尤其适用于存在大量潜在匹配的文本，特别是长模式的情况。

## 3. 拉宾-卡普（Rabin-Karp）算法

拉宾-卡普算法使用哈希技术更高效地查找模式匹配。它不是逐个比较字符，而是比较模式和文本子串的哈希值。

### 拉宾-卡普算法的工作原理

1. 计算模式的哈希值
2. 使用滚动哈希函数计算文本中所有长度为m的子串的哈希值
3. 比较模式的哈希值与每个子串的哈希值
4. 如果哈希值匹配，则逐字符验证实际字符串

### 实现滚动哈希函数

滚动哈希函数允许我们通过当前子串的哈希值，在常数时间内计算下一个子串的哈希值：

```go
// 移除最左边的字符并添加最右边的字符
newHash = (oldHash - oldChar * pow) * base + newChar
```

### 在Go语言中实现拉宾-卡普算法

```go
func RabinKarpSearch(text, pattern string) []int {
    matches := []int{}
    
    // 处理边界情况
    if len(pattern) == 0 || len(text) < len(pattern) {
        return matches
    }
    
    n := len(text)
    m := len(pattern)
    
    // 大质数以减少哈希冲突
    prime := 101
    
    // 哈希函数的基础值
    base := 256
    
    // 模式的哈希值和初始窗口的哈希值
    patternHash := 0
    windowHash := 0
    
    // 所需的base最高次幂
    h := 1
    for i := 0; i < m-1; i++ {
        h = (h * base) % prime
    }
    
    // 计算初始哈希值
    for i := 0; i < m; i++ {
        patternHash = (base*patternHash + int(pattern[i])) % prime
        windowHash = (base*windowHash + int(text[i])) % prime
    }
    
    // 逐个滑动模式
    for i := 0; i <= n-m; i++ {
        // 检查哈希值是否匹配
        if patternHash == windowHash {
            // 逐字符验证匹配
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
            windowHash = (base*(windowHash-int(text[i])*h) + int(text[i+m])) % prime
            
            // 确保哈希值为正
            if windowHash < 0 {
                windowHash += prime
            }
        }
    }
    
    return matches
}
```

### 拉宾-卡普算法的时间复杂度

- **平均情况时间复杂度**：O(n+m)，其中n是文本长度，m是模式长度
- **最坏情况时间复杂度**：O(n×m)，当存在大量哈希冲突时
- **空间复杂度**：O(k)，其中k是找到的匹配数量

拉宾-卡普算法特别适用于多模式搜索和抄袭检测。

## 算法对比

| 算法 | 平均时间复杂度 | 最坏时间复杂度 | 空间复杂度 | 优点 | 缺点 |
|-----------|----------------|----------------|--------------|------|------|
| 暴力     | O(n×m)         | O(n×m)         | O(1)         | 简单，开销低 | 大字符串效率差 |
| KMP       | O(n+m)         | O(n+m)         | O(m)         | 非常高效，无需回溯 | 较复杂，需要预处理 |
| 拉宾-卡普 | O(n+m)         | O(n×m)         | O(1)         | 多模式搜索效果好 | 可能发生哈希冲突 |

## 实际应用

### 1. 文本编辑器

模式匹配对于文本编辑器中的“查找”和“替换”操作至关重要。

### 2. 生物信息学

DNA序列匹配使用模式匹配在基因组中查找基因序列。

### 3. 入侵检测

网络安全系统使用模式匹配识别网络流量中的可疑模式。

### 4. 抄袭检测

文档相似性检查使用模式匹配查找复制内容。

## 进一步阅读

1. [克努斯-莫里斯-普拉特算法（GeeksforGeeks）](https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/)
2. [拉宾-卡普算法（GeeksforGeeks）](https://www.geeksforgeeks.org/rabin-karp-algorithm-for-pattern-searching/)
3. [字符串匹配算法（维基百科）](https://en.wikipedia.org/wiki/String-searching_algorithm)
4. [高级字符串搜索（斯坦福CS166）](https://web.stanford.edu/class/cs166/)