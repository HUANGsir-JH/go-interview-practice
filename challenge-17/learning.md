# 回文检查器学习资料

## Go 中的字符串操作

在此挑战中，你将学习 Go 语言中的字符串操作。Go 通过 `strings` 包和其他内置函数提供了对字符串操作的强大支持。

### 基本字符串操作

#### 字符串长度

你可以使用内置的 `len()` 函数获取字符串长度：

```go
str := "Hello, World!"
length := len(str)  // length 为 13
```

#### 字符串比较

可以使用标准比较运算符来比较字符串：

```go
str1 := "apple"
str2 := "banana"
if str1 == str2 {
    // 字符串相等
}
```

### 字符串操作

#### 大小写转换

`strings` 包提供了在大写和小写之间转换的函数：

```go
import "strings"

str := "Hello"
lower := strings.ToLower(str)  // "hello"
upper := strings.ToUpper(str)  // "HELLO"
```

#### 删除字符

要从字符串中删除字符，你可以：

1. 使用 `strings.ReplaceAll()` 将字符替换为空字符串：

```go
import "strings"

str := "Hello, World!"
withoutCommas := strings.ReplaceAll(str, ",", "")  // "Hello World!"
```

2. 构建一个新字符串，仅保留你想要的字符：

```go
func removeNonAlphanumeric(s string) string {
    var result strings.Builder
    for _, r := range s {
        if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') {
            result.WriteRune(r)
        }
    }
    return result.String()
}
```

### 使用 Rune

Go 将 Unicode 字符表示为 rune（int32 的别名）。当使用 range 循环遍历字符串时，你会得到 rune 而不是字节：

```go
str := "Hello, 世界"
for i, r := range str {
    fmt.Printf("%d: %c (%d)\n", i, r, r)
}
```

### 反转字符串

Go 没有内置的反转字符串函数，但你可以自己编写一个：

```go
func reverseString(s string) string {
    runes := []rune(s)
    for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
        runes[i], runes[j] = runes[j], runes[i]
    }
    return string(runes)
}
```

### 检查回文

要检查字符串是否为回文：

1. 清理字符串（移除空格、标点符号，并转换为小写）
2. 检查清理后的字符串正向和反向是否相同

```go
func isPalindrome(s string) bool {
    // 转换为小写
    s = strings.ToLower(s)
    
    // 移除非字母数字字符
    var cleaned strings.Builder
    for _, r := range s {
        if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
            cleaned.WriteRune(r)
        }
    }
    
    // 获取清理后的字符串
    cleanedStr := cleaned.String()
    
    // 检查是否为回文
    for i := 0; i < len(cleanedStr)/2; i++ {
        if cleanedStr[i] != cleanedStr[len(cleanedStr)-1-i] {
            return false
        }
    }
    
    return true
}
```

## 性能考虑

### strings.Builder 与字符串拼接

在构建字符串时，应使用 `strings.Builder` 而不是用 `+` 拼接，以避免创建多个临时字符串：

```go
// 效率较低
result := ""
for i := 0; i < 1000; i++ {
    result += "a"  // 每次都创建新字符串
}

// 效率较高
var builder strings.Builder
for i := 0; i < 1000; i++ {
    builder.WriteString("a")
}
result := builder.String()
```

### Unicode 考虑

请记住，Go 中的字符串是字节序列，而不是字符序列。处理 Unicode 字符时，应转换为 rune：

```go
str := "Hello, 世界"
runes := []rune(str)
```

## 进一步阅读

- [Go by Example: 字符串](https://gobyexample.com/strings)
- [strings 包文档](https://pkg.go.dev/strings)
- [unicode 包文档](https://pkg.go.dev/unicode)
- [Go 博客：Go 中的字符串、字节、rune 和字符](https://blog.golang.org/strings)