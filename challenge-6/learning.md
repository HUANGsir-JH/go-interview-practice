# 词频统计学习资料

## Go语言中的映射（Maps）

映射是Go语言内置的数据结构，用于将键与值关联起来，类似于其他语言中的字典、哈希表或关联数组。

### 基本映射操作

```go
// 声明一个字符串键和整数值的映射
wordFrequency := make(map[string]int)

// 设置一个值
wordFrequency["hello"] = 1

// 更新一个值
wordFrequency["hello"]++

// 获取一个值
count := wordFrequency["hello"]

// 检查键是否存在
count, exists := wordFrequency["world"]
if exists {
    fmt.Println("'world' 找到，计数为:", count)
} else {
    fmt.Println("'world' 在映射中未找到")
}

// 删除一个键
delete(wordFrequency, "hello")

// 遍历映射
for word, count := range wordFrequency {
    fmt.Printf("%s: %d\n", word, count)
}
```

## Go语言中的字符串处理

Go语言在`strings`包中提供了多种字符串操作函数。

### 常见字符串操作

```go
import "strings"

// 转换为小写
lowercase := strings.ToLower("Hello")  // "hello"

// 分割字符串
words := strings.Split("hello world", " ")  // ["hello", "world"]

// 连接字符串
joined := strings.Join([]string{"hello", "world"}, " ")  // "hello world"

// 替换所有出现
replaced := strings.ReplaceAll("hello, hello!", ",", "")  // "hello hello!"

// 包含子串
hasPrefix := strings.Contains("hello world", "hello")  // true

// 去除空白字符
trimmed := strings.TrimSpace("  hello  ")  // "hello"
```

## 正则表达式用于高级字符串处理

对于更复杂的字符串处理，Go语言的`regexp`包提供了强大的模式匹配功能：

```go
import "regexp"

// 创建一个仅匹配字母和数字的正则表达式
re := regexp.MustCompile(`[^a-zA-Z0-9]+`)

// 将所有非字母数字字符替换为空格
cleaned := re.ReplaceAllString("Hello, world! 123", " ")  // "Hello world 123"

// 使用正则表达式分割
words := re.Split("Hello,world!123", -1)  // ["Hello", "world", "123"]
```

## 效率考虑

在处理大文本时：

1. **预分配**：如果知道映射的大致大小，可以预先指定容量：
   ```go
   wordFrequency := make(map[string]int, 1000)  // 预分配1000个单词的空间
   ```

2. **Builder模式**：对于复杂的字符串操作，使用`strings.Builder`：
   ```go
   var builder strings.Builder
   for _, word := range words {
       builder.WriteString(word)
       builder.WriteString(" ")
   }
   result := builder.String()
   ```

3. **单次遍历处理**：尽可能避免对同一数据进行多次迭代

## 词频统计核心概念

实现词频统计时需要理解的关键概念：

- **文本归一化**：将文本转换为一致格式（转为小写、去除标点符号）
- **词边界识别**：确定词语的起始和结束位置
- **字符过滤**：决定哪些字符可作为有效单词的一部分
- **频率追踪**：使用映射高效统计出现次数
- **内存优化**：在可能的情况下预先分配映射空间

### 处理步骤
1. 归一化输入文本（大小写转换）
2. 清理文本，移除或替换不需要的字符
3. 将文本拆分为独立的单词
4. 使用映射统计每个单词的频率
5. 处理边缘情况（空字符串、空白字符）

## 相关Go语言概念

- **哈希映射**：Go语言的映射基于哈希表实现，平均查找时间复杂度为O(1)
- **字符串为UTF-8编码**：Go字符串默认采用UTF-8编码，处理非ASCII字符时需特别注意
- **不可变性**：Go中的字符串是不可变的，因此像`ToLower()`这样的操作会创建新字符串
- **Rune类型**：为了正确处理Unicode字符，建议使用`[]rune`而非字节来处理字符

## 进一步阅读

- [Go语言中的映射](https://blog.golang.org/maps)
- [Go语言中的字符串、字节、Rune与字符](https://blog.golang.org/strings)
- [Go语言中的正则表达式](https://gobyexample.com/regular-expressions)