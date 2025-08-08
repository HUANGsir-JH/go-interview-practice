# 回文检查学习材料

## Go中的字符串和字符操作

这个挑战涉及高级字符串操作，包括筛选字符和处理大小写敏感性。

### 字符分类

`unicode` 包对于字符分类至关重要。

- `unicode.IsLetter(r rune)`：检查一个rune是否是字母。
- `unicode.IsDigit(r rune)`：检查一个rune是否是数字。
- `unicode.IsNumber(r rune)`：与`IsDigit`类似，但更通用。
- `unicode.ToLower(r rune)`：将一个rune转换为小写。

示例：
```go
import "unicode"

for _, r := range "A man, a plan, 123" {
    if unicode.IsLetter(r) || unicode.IsDigit(r) {
        // 处理字母数字字符
    }
}
```

### 高效构建字符串

重复使用 `+` 连接字符串可能效率低下，因为它每次操作都会在内存中创建一个新字符串。`strings.Builder` 类型是构建字符串的更高效方法。

```go
import "strings"

var builder strings.Builder
for _, r := range "example" {
    builder.WriteRune(r)
}
finalString := builder.String()
```

### 算法：双指针技术

双指针技术是处理序列（如数组、切片或字符串）问题的常用且高效的算法。

1.  **初始化**：
    -   `left` 指针从序列的开头（索引 0）开始。
    -   `right` 指针从序列的末尾（索引 `len(seq) - 1`）开始。

2.  **迭代**：
    -   循环在 `left < right` 的情况下继续。
    -   在每次迭代中，比较 `seq[left]` 和 `seq[right]`。
    -   如果它们不相等，则不满足条件（例如，不是回文）。
    -   将指针向中心移动：`left++`，`right--`。

3.  **终止**：
    -   如果循环完成，则意味着整个序列都满足条件。

该技术的时间复杂度为 O(n)，因为它只需要对序列进行单次遍历。

### 应用于回文检查

1.  **筛选字符串**：创建一个新的、干净的字符串，仅包含小写字母数字字符。
2.  **应用双指针**：在清理后的字符串上使用双指针技术检查它是否是回文。

### 替代方案：反转和比较

另一种方法是：
1.  如上所述筛选字符串。
2.  创建筛选后字符串的反转版本。
3.  将筛选后的字符串与其反转版本进行比较。如果它们相同，则为回文。

虽然概念上更简单，但这可能性能较差，因为它需要创建第二个新字符串。

## 进一步阅读

- [Go by Example: String Functions](https://gobyexample.com/string-functions)
- [strings.Builder documentation](https://pkg.go.dev/strings#Builder)
- [unicode package documentation](https://pkg.go.dev/unicode)