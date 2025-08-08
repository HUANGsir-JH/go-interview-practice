# 挑战 26 提示：正则表达式文本处理器

## 提示 1：电子邮件提取模式
构建一个正则表达式模式来匹配有效的电子邮件地址：
```go
import "regexp"

func ExtractEmails(text string) []string {
    // 电子邮件模式：本地部分 @ 域名部分
    emailPattern := `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
    re := regexp.MustCompile(emailPattern)
    
    matches := re.FindAllString(text, -1)
    return matches
}

// 更全面的电子邮件模式
var emailRegex = regexp.MustCompile(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`)
```

## 提示 2：电话号码验证
使用括号和连字符验证精确的电话号码格式：
```go
func ValidatePhone(phone string) bool {
    // 模式：(XXX) XXX-XXXX，其中 X 为数字
    phonePattern := `^\(\d{3}\) \d{3}-\d{4}$`
    re := regexp.MustCompile(phonePattern)
    
    return re.MatchString(phone)
}

// 使用命名组以提高清晰度的替代方案
var phoneRegex = regexp.MustCompile(`^\((?P<area>\d{3})\) (?P<exchange>\d{3})-(?P<number>\d{4})$`)

func ValidatePhoneDetailed(phone string) bool {
    return phoneRegex.MatchString(phone)
}
```

## 提示 3：信用卡号屏蔽
两种方法在保留最后四位数字的同时屏蔽信用卡号：

**方法 1：提取数字，屏蔽中间部分，再恢复格式**
- 使用 `\D` 正则表达式移除非数字字符，屏蔽中间数字，保留原始格式

**方法 2：直接使用前瞻进行正则替换**
- 模式 `\d(?=.*\d{3})` 匹配后面至少还有三位数字的数字
- 将匹配到的数字替换为 "X"，自动保留最后四位

```go
// 简单的正则表达式方法
pattern := `\d(?=.*\d{3})`
re := regexp.MustCompile(pattern)
return re.ReplaceAllString(cardNumber, "X")
```
```

## 提示 4：日志条目解析
使用捕获组解析结构化日志条目：

**关键概念：**
- 使用 `^` 和 `$` 锚点匹配整行
- `(?P<name>pattern)` 创建命名捕获组
- `\d{4}` 匹配恰好四位数字，`\w+` 匹配单词字符
- 使用 `re.SubexpNames()` 将组名映射到值

```go
// 模式：YYYY-MM-DD HH:MM:SS LEVEL Message
pattern := `^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.+)$`

// 使用命名组提取
names := re.SubexpNames()
for i, name := range names {
    if name != "" && i < len(matches) {
        result[name] = matches[i]
    }
}
```
```

## 提示 5：URL 提取
提取支持多种协议和查询参数的 URL：
```go
func ExtractURLs(text string) []string {
    // 支持 http/https 及可选查询参数的 URL 模式
    urlPattern := `https?://[a-zA-Z0-9._/-]+(?:\?[a-zA-Z0-9=&%._-]*)?`
    re := regexp.MustCompile(urlPattern)
    
    matches := re.FindAllString(text, -1)
    return matches
}

// 更全面的 URL 模式
var urlRegex = regexp.MustCompile(`https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%._-])*)?(?:#(?:\w)*)?`)

func ExtractURLsComprehensive(text string) []string {
    return urlRegex.FindAllString(text, -1)
}
```

## 提示 6：通过预编译正则表达式优化性能
一次性编译模式以获得更好的性能：
```go
var (
    emailRegex      = regexp.MustCompile(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`)
    phoneRegex      = regexp.MustCompile(`^\(\d{3}\) \d{3}-\d{4}$`)
    creditCardRegex = regexp.MustCompile(`\d(?=.*\d{3})`)
    logRegex        = regexp.MustCompile(`^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.+)$`)
    urlRegex        = regexp.MustCompile(`https?://[a-zA-Z0-9._/-]+(?:\?[a-zA-Z0-9=&%._-]*)?`)
)

func ExtractEmailsOptimized(text string) []string {
    return emailRegex.FindAllString(text, -1)
}

func ValidatePhoneOptimized(phone string) bool {
    return phoneRegex.MatchString(phone)
}
```

## 提示 7：边缘情况与错误处理
处理各种边缘情况和无效输入：
```go
func ExtractEmailsSafe(text string) []string {
    if text == "" {
        return []string{}
    }
    
    emails := emailRegex.FindAllString(text, -1)
    if emails == nil {
        return []string{}
    }
    
    return emails
}

func ParseLogEntrySafe(logLine string) map[string]string {
    if strings.TrimSpace(logLine) == "" {
        return nil
    }
    
    matches := logRegex.FindStringSubmatch(logLine)
    if matches == nil {
        return nil
    }
    
    result := make(map[string]string)
    names := logRegex.SubexpNames()
    
    for i, name := range names {
        if name != "" && i < len(matches) {
            result[name] = strings.TrimSpace(matches[i])
        }
    }
    
    return result
}

func MaskCreditCardSafe(cardNumber string) string {
    if cardNumber == "" {
        return ""
    }
    
    // 检查是否为有效的卡号格式
    digitsOnly := regexp.MustCompile(`\D`).ReplaceAllString(cardNumber, "")
    if len(digitsOnly) < 4 || len(digitsOnly) > 19 {
        return cardNumber // 如果无效则返回原值
    }
    
    return creditCardRegex.ReplaceAllString(cardNumber, "X")
}
```

## 关键正则表达式概念：
- **字符类**：`[a-zA-Z0-9]` 表示字母数字字符
- **量词**：`+`（一个或多个），`*`（零个或多个），`{n}`（恰好 n 个）
- **锚点**：`^`（字符串开头），`$`（字符串结尾），`\b`（单词边界）
- **分组**：`()` 用于捕获组，`(?P<name>...)` 用于命名组
- **前瞻**：`(?=...)` 用于正向前瞻断言
- **转义**：`\` 用于转义特殊字符如 `.` 或 `?`