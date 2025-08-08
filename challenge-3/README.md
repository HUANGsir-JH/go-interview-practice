[查看排行榜](SCOREBOARD.md)

# 挑战 3：回文检查

## 问题描述

编写一个函数 `IsPalindrome`，检查给定字符串是否是回文，忽略大小写和非字母数字字符。

## 函数签名

```go
func IsPalindrome(s string) bool
```

## 输入格式

- 包含字符串 `s` 的单行。

## 输出格式

- 如果字符串是回文，则为 `true`，否则为 `false`。

## 约束条件

- `1 <= len(s) <= 2 * 10^5`
- 字符串由可打印的ASCII字符组成。

## 示例输入和输出

### 示例输入 1

```
A man, a plan, a canal: Panama
```

### 示例输出 1

```
true
```

### 示例输入 2

```
race a car
```

### 示例输出 2

```
false
```

## 如何运行

- **Fork** 仓库。
- **Clone** 您的 fork 到本地机器。
- **Create** 在 `challenge-3/submissions/` 内创建一个以您的 GitHub 用户名命名的目录。
- **Copy** 将 `solution-template.go` 文件复制到您的提交目录中。
- **Implement** 实现 `IsPalindrome` 函数。
- **Test** 通过运行测试文件在本地测试您的解决方案。
- **Commit** 并 **push** 您的代码到您的 fork。
- **Create** 创建拉取请求以提交您的解决方案。

## 如何在本地测试您的解决方案

导航到 `challenge-3/` 目录并运行：

```bash
go test -v
```