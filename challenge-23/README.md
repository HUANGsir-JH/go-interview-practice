[查看排行榜](SCOREBOARD.md)

# 挑战 23：字符串模式匹配

## 问题描述

实现高效的字符串模式匹配算法，以查找文本中所有模式出现的位置。在此挑战中，你需要实现三种不同的模式匹配算法：

1. `NaivePatternMatch` - 一种简单的暴力方法，检查每个可能的位置。
2. `KMPSearch` - Knuth-Morris-Pratt 算法，通过使用预处理的前缀表避免不必要的比较。
3. `RabinKarpSearch` - Rabin-Karp 算法，利用哈希技术高效地查找模式。

## 函数签名

```go
func NaivePatternMatch(text, pattern string) []int
func KMPSearch(text, pattern string) []int
func RabinKarpSearch(text, pattern string) []int
```

## 输入格式

- `text` - 要搜索模式的主要文本字符串。
- `pattern` - 要搜索的模式字符串。

## 输出格式

- 所有函数应返回一个整数切片，包含文本中所有模式出现位置的起始索引。
- 如果未找到匹配项，则返回空切片。
- 索引应为 0 基（第一个字符位于位置 0）。

## 要求

1. `NaivePatternMatch` 应实现一个直接的暴力算法。
2. `KMPSearch` 应实现 Knuth-Morris-Pratt 算法。
3. `RabinKarpSearch` 应实现 Rabin-Karp 算法。
4. 三个函数都应返回相同且正确的结果。
5. 注意边界情况，如空字符串、模式长度超过文本等情况。

## 示例输入与输出

### 示例输入 1

```
NaivePatternMatch("ABABDABACDABABCABAB", "ABABCABAB")
```

### 示例输出 1

```
[10]
```

### 示例输入 2

```
KMPSearch("AABAACAADAABAABA", "AABA")
```

### 示例输出 2

```
[0, 9, 12]
```

### 示例输入 3

```
RabinKarpSearch("GEEKSFORGEEKS", "GEEK")
```

### 示例输出 3

```
[0, 8]
```

### 示例输入 4

```
NaivePatternMatch("AAAAAA", "AA")
```

### 示例输出 4

```
[0, 1, 2, 3, 4]
```

## 指导说明

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-23/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的函数。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-23/` 目录下运行以下命令：

```bash
go test -v
```

## 性能预期

- **朴素算法**：时间复杂度为 O(n*m)，其中 n 是文本长度，m 是模式长度。
- **KMP 算法**：时间复杂度为 O(n+m)。
- **Rabin-Karp 算法**：平均情况下时间复杂度为 O(n+m)，最坏情况下为 O(n*m)。