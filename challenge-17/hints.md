# 回文检查器提示

## 提示 1：理解回文
回文正读和反读都相同。示例："racecar"，"A man a plan a canal Panama"（忽略空格和大小写）。

## 提示 2：字符串规范化
将字符串转换为小写并移除非字母数字字符：
```go
func normalize(s string) string {
    var result strings.Builder
    for _, r := range s {
        if unicode.IsLetter(r) || unicode.IsDigit(r) {
            result.WriteRune(unicode.ToLower(r))
        }
    }
    return result.String()
}
```

## 提示 3：双指针方法
使用两个指针从两端向中间移动：
```go
func isPalindrome(s string) bool {
    normalized := normalize(s)
    left, right := 0, len(normalized)-1
    
    for left < right {
        if normalized[left] != normalized[right] {
            return false
        }
        left++
        right--
    }
    return true
}
```

## 提示 4：Rune 转换替代方案
为了 Unicode 安全性，转换为 runes：
```go
runes := []rune(normalized)
```

## 提示 5：简单的反转比较
替代方法——反转字符串并进行比较：
```go
func reverse(s string) string {
    runes := []rune(s)
    for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
        runes[i], runes[j] = runes[j], runes[i]
    }
    return string(runes)
}
```