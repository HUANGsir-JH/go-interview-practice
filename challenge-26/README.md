# 挑战 26：正则表达式文本处理器

## 问题描述

在此挑战中，你将实现一个使用正则表达式的文本处理工具，用于从各种文本格式中提取、验证和转换数据。

你的任务是创建一个正则表达式处理器，能够：

1. 从文本中提取特定的数据模式（电子邮件、电话号码、日期等）
2. 验证输入字符串是否符合特定格式
3. 基于模式匹配替换或转换文本
4. 解析结构化文本，如日志或 CSV 数据

## 函数签名

你需要实现以下函数：

```go
// ExtractEmails 从文本中提取所有有效的电子邮件地址
func ExtractEmails(text string) []string

// ValidatePhone 检查字符串是否为有效电话号码格式 (XXX) XXX-XXXX
func ValidatePhone(phone string) bool

// MaskCreditCard 将信用卡号除最后 4 位外的所有数字替换为 "X"
// 示例： "1234-5678-9012-3456" -> "XXXX-XXXX-XXXX-3456"
func MaskCreditCard(cardNumber string) string

// ParseLogEntry 解析格式为：
// "YYYY-MM-DD HH:MM:SS LEVEL Message" 的日志条目
// 返回包含键值对的 map： "date", "time", "level", "message"
func ParseLogEntry(logLine string) map[string]string

// ExtractURLs 从文本中提取所有有效的 URL
func ExtractURLs(text string) []string
```

## 输入/输出示例

### ExtractEmails
- 输入： `"Contact us at support@example.com or sales@company.co.uk for more info."`
- 输出： `["support@example.com", "sales@company.co.uk"]`

### ValidatePhone
- 输入： `"(555) 123-4567"`
- 输出： `true`
- 输入： `"555-123-4567"`
- 输出： `false`

### MaskCreditCard
- 输入： `"1234-5678-9012-3456"`
- 输出： `"XXXX-XXXX-XXXX-3456"`
- 输入： `"1234567890123456"`
- 输出： `"XXXXXXXXXXXX3456"`

### ParseLogEntry
- 输入： `"2023-11-15 14:23:45 INFO Server started on port 8080"`
- 输出： 
```go
map[string]string{
    "date":    "2023-11-15",
    "time":    "14:23:45",
    "level":   "INFO",
    "message": "Server started on port 8080",
}
```

### ExtractURLs
- 输入： `"Visit https://golang.org and http://example.com/page?q=123 for more information."`
- 输出： `["https://golang.org", "http://example.com/page?q=123"]`

## 约束条件

- 你的解决方案应适当处理边界情况
- 正则表达式应高效，避免过度回溯
- 编译正则表达式一次并重复使用以提高性能
- 对于电子邮件验证，使用合理的正则表达式覆盖常见电子邮件格式

## 评估标准

- 正确性：你的解决方案是否处理了所有要求的情况？
- 效率：你的正则表达式是否经过优化？
- 代码质量：代码结构是否良好且有文档说明？
- 错误处理：代码是否能优雅地处理无效输入？

## 学习资源

参见 [learning.md](learning.md) 文档，获取在 Go 中使用正则表达式的全面指南。

## 提示

1. Go 中的 `regexp` 包提供了完整的正则表达式功能
2. 对于已知有效的模式，使用 `MustCompile` 可简化错误处理
3. 记得处理模式中的特殊字符
4. 对于复杂模式，考虑将其分解为更小的部分
5. 使用多种输入测试你的正则表达式，包括边界情况