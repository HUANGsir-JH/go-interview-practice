# 正则表达式处理器学习资料

## Go 中的正则表达式

本挑战聚焦于使用 Go 的 `regexp` 包来实现模式匹配和文本操作。

### 理解 Go 中的正则表达式

正则表达式（regex）是用于匹配字符串中字符组合的强大模式。Go 通过标准库的 `regexp` 包提供了强大的正则表达式支持。

```go
import "regexp"
```

### 基础模式匹配

使用正则表达式的最简单方法是检查某个模式是否存在于字符串中：

```go
// 编译正则表达式模式
pattern := `\d+`  // 匹配一个或多个数字
re, err := regexp.Compile(pattern)
if err != nil {
    // 处理错误
}

// 检查模式是否匹配字符串
matched := re.MatchString("123 Main St")  // 返回 true
```

对于快速操作，可以使用包级别的函数：

```go
matched, err := regexp.MatchString(`\d+`, "123 Main St")
```

### 常见的正则表达式模式

以下是一些常用的模式：

| 模式 | 描述 | 示例 |
|------|------|------|
| `\d` | 匹配数字字符 | `\d+` 在 "The answer is 42" 中匹配 "42" |
| `\D` | 匹配非数字字符 | `\D+` 在 "The answer is 42" 中匹配 "The answer is " |
| `\w` | 匹配单词字符（字母数字 + 下划线） | `\w+` 在 "Hello_123!" 中匹配 "Hello_123" |
| `\W` | 匹配非单词字符 | `\W+` 在 "abc!@#def" 中匹配 "!@#" |
| `\s` | 匹配空白字符 | `\s+` 匹配单词之间的空格 |
| `\S` | 匹配非空白字符 | `\S+` 匹配每个单词 |
| `.` | 匹配除换行符外的任意字符 | `a.b` 匹配 "acb", "adb" 等 |
| `^` | 匹配字符串的开头 | `^Hello` 仅在开头匹配 "Hello" |
| `$` | 匹配字符串的结尾 | `world$` 仅在结尾匹配 "world" |
| `[abc]` | 匹配集合中的任意字符 | `[aeiou]` 匹配任意元音 |
| `[^abc]` | 匹配集合外的任意字符 | `[^aeiou]` 匹配任意非元音 |
| `a*` | 匹配 'a' 的 0 次或多次 | `a*` 匹配 "", "a", "aa" 等 |
| `a+` | 匹配 'a' 的 1 次或多次 | `a+` 匹配 "a", "aa" 等但不包括 "" |
| `a?` | 匹配 'a' 的 0 次或 1 次 | `a?` 匹配 "" 或 "a" |
| `a{n}` | 匹配 'a' 的恰好 n 次 | `a{3}` 匹配 "aaa" |
| `a{n,}` | 匹配 'a' 的 n 次或更多次 | `a{2,}` 匹配 "aa", "aaa" 等 |
| `a{n,m}` | 匹配 'a' 的 n 到 m 次 | `a{2,4}` 匹配 "aa", "aaa", 或 "aaaa" |
| `a\|b` | 匹配 'a' 或 'b' | `cat\|dog` 匹配 "cat" 或 "dog" |
| `()` | 分组模式并捕获匹配内容 | `(abc)+` 匹配 "abc", "abcabc" 等 |

### 查找匹配项

查找字符串中所有匹配项：

```go
re := regexp.MustCompile(`\d+`)  // MustCompile 在出错时会 panic
matches := re.FindAllString("There are 15 apples and 25 oranges", -1)
// matches = ["15", "25"]
```

查找第一个匹配项：

```go
match := re.FindString("There are 15 apples and 25 oranges")
// match = "15"
```

### 捕获组

捕获组允许你提取匹配中的特定部分：

```go
re := regexp.MustCompile(`(\w+)@(\w+)\.(\w+)`)
matches := re.FindStringSubmatch("contact us at user@example.com for more info")
// matches = ["user@example.com", "user", "example", "com"]
```

第一个元素是完整匹配，后面是每个捕获组。

获取匹配项的索引位置：

```go
indexes := re.FindStringSubmatchIndex("contact us at user@example.com")
// indexes 包含每个匹配项的起始和结束位置
```

### 替换匹配项

将所有匹配项替换为新字符串：

```go
re := regexp.MustCompile(`\d+`)
result := re.ReplaceAllString("There are 15 apples and 25 oranges", "XX")
// result = "There are XX apples and XX oranges"
```

使用函数动态确定替换内容：

```go
re := regexp.MustCompile(`\d+`)
result := re.ReplaceAllStringFunc("15 apples and 25 oranges", func(s string) string {
    // 将字符串数字转换为整数，翻倍后返回字符串形式
    n, _ := strconv.Atoi(s)
    return strconv.Itoa(n * 2)
})
// result = "30 apples and 50 oranges"
```

### 使用命名捕获组

命名捕获组使你的正则表达式更具可读性：

```go
re := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})`)
matches := re.FindStringSubmatch("The date is 2023-11-15")
// matches = ["2023-11-15", "2023", "11", "15"]

// 按名称提取
yearIndex := re.SubexpIndex("year")
year := matches[yearIndex]  // "2023"
```

### 字符串分割

基于正则表达式模式分割字符串：

```go
re := regexp.MustCompile(`\s+`)  // 匹配一个或多个空白字符
parts := re.Split("Hello   world  !  ", -1)
// parts = ["Hello", "world", "!", ""]
```

### 编译标志

通过标志修改正则表达式的运行行为：

```go
// 不区分大小写的匹配
re := regexp.MustCompile(`(?i)hello`)
matched := re.MatchString("Hello")  // true

// 多行模式 - ^ 和 $ 匹配行的开始和结束
re := regexp.MustCompile(`(?m)^start`)
matched := re.MatchString("line1\nstart of line2")  // true

// 同时使用多个标志
re := regexp.MustCompile(`(?im)^hello$`)
```

### 输入格式验证

正则表达式非常适合用于验证输入格式：

```go
// 邮箱验证（简化版）
emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
valid := emailRegex.MatchString("user@example.com")  // true

// 电话号码验证（美国格式）
phoneRegex := regexp.MustCompile(`^\(\d{3}\) \d{3}-\d{4}$`)
valid := phoneRegex.MatchString("(555) 123-4567")  // true

// URL 验证（简化版）
urlRegex := regexp.MustCompile(`^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9_.-]*)*$`)
valid := urlRegex.MatchString("https://www.example.com/path")  // true
```

### 性能考虑

1. **一次编译，多次使用**：编译正则表达式成本较高，因此应只编译一次并重复使用已编译的模式。

```go
// 不好的做法
for _, s := range strings {
    matched, _ := regexp.MatchString(pattern, s)  // 每次迭代都重新编译
}

// 好的做法
re := regexp.MustCompile(pattern)
for _, s := range strings {
    matched := re.MatchString(s)  // 重用已编译的模式
}
```

2. **避免过度回溯**：包含大量重复操作符的复杂模式可能导致过度回溯，从而影响性能。

3. **使用具体模式**：更具体的模式通常比过于通用的模式性能更好。

### 处理复杂模式

对于复杂的文本处理任务，可将任务分解为多个正则表达式：

```go
// 提取 HTML 标签及其内容
re := regexp.MustCompile(`<([a-z]+)>(.*?)</\1>`)
matches := re.FindAllStringSubmatch("<p>First paragraph</p><div>Content</div>", -1)
// matches = [["<p>First paragraph</p>", "p", "First paragraph"], ["<div>Content</div>", "div", "Content"]]
```

### 正则表达式调试

调试复杂正则表达式时，应将其拆分并逐一测试各部分：

```go
// 复杂的正则表达式
fullPattern := `^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}:\d{2})$`

// 拆分
datePattern := `^\d{4}-\d{2}-\d{2}`
timePattern := `\d{2}:\d{2}:\d{2}`
timezonePattern := `[+-]\d{2}:\d{2}$`

// 测试各部分
dateRe := regexp.MustCompile(datePattern)
timeRe := regexp.MustCompile(timePattern)
tzRe := regexp.MustCompile(timezonePattern)

dateMatches := dateRe.FindString("2023-11-15T14:30:45+02:00")  // "2023-11-15"
timeMatches := timeRe.FindString("2023-11-15T14:30:45+02:00")  // "14:30:45"
tzMatches := tzRe.FindString("2023-11-15T14:30:45+02:00")      // "+02:00"
```

### 实践示例：日志分析器

以下是一个使用正则表达式解析日志条目的实用示例：

```go
package main

import (
    "fmt"
    "regexp"
    "strings"
)

func main() {
    logLines := []string{
        "2023-11-15 14:23:45 INFO Server started on port 8080",
        "2023-11-15 14:24:12 ERROR Failed to connect to database: timeout",
        "2023-11-15 14:25:01 WARNING High memory usage: 85%",
    }

    // 定义用于解析日志条目的正则表达式
    logPattern := regexp.MustCompile(`^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\w+) (.+)$`)

    for _, line := range logLines {
        matches := logPattern.FindStringSubmatch(line)
        if len(matches) == 5 {
            date := matches[1]
            time := matches[2]
            level := matches[3]
            message := matches[4]

            fmt.Printf("Date: %s, Time: %s, Level: %s, Message: %s\n", 
                      date, time, level, message)
            
            // 对错误日志进行额外处理
            if level == "ERROR" {
                errorPattern := regexp.MustCompile(`Failed to (.*?): (.*)`)
                errorMatches := errorPattern.FindStringSubmatch(message)
                if len(errorMatches) == 3 {
                    action := errorMatches[1]
                    reason := errorMatches[2]
                    fmt.Printf("  Error details - Action: %s, Reason: %s\n", action, reason)
                }
            }
        }
    }
}
```

### 进一步阅读

- [Go regexp 包文档](https://golang.org/pkg/regexp/)
- [正则表达式快速入门](https://github.com/google/re2/wiki/Syntax)
- [正则表达式测试工具](https://regex101.com/)
- [《Go 编程语言》——关于正则表达式的章节](https://www.gopl.io/)