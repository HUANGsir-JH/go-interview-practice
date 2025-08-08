[查看排行榜](SCOREBOARD.md)

# 挑战 24：动态规划 - 最长递增子序列

## 问题描述

最长递增子序列（LIS）问题是经典的动态规划问题。给定一个整数序列，找出最长的子序列，使得子序列中的所有元素按递增顺序排列。子序列是指可以从另一个序列中删除一些或不删除任何元素，而不改变剩余元素顺序得到的序列。

在此挑战中，你将实现三种不同的方法来解决 LIS 问题：

1. `DPLongestIncreasingSubsequence` - 标准的动态规划解决方案，时间复杂度为 O(n²)。
2. `OptimizedLIS` - 使用二分查找优化的解决方案，时间复杂度为 O(n log n)。
3. `GetLISElements` - 返回 LIS 的实际元素，而不仅仅是其长度。

## 函数签名

```go
func DPLongestIncreasingSubsequence(nums []int) int
func OptimizedLIS(nums []int) int
func GetLISElements(nums []int) []int
```

## 输入格式

- `nums` - 表示序列的整数切片。

## 输出格式

- `DPLongestIncreasingSubsequence` - 返回一个整数，表示 LIS 的长度。
- `OptimizedLIS` - 返回一个整数，表示 LIS 的长度。
- `GetLISElements` - 返回一个整数切片，表示某个可能的 LIS 的元素。

## 要求

1. `DPLongestIncreasingSubsequence` 应实现标准的动态规划解决方案，时间复杂度为 O(n²)。
2. `OptimizedLIS` 应实现优化的解决方案，时间复杂度为 O(n log n)。
3. `GetLISElements` 应返回 LIS 的实际元素，而不仅仅是其长度。
4. 处理空切片或仅包含单个元素的切片等边界情况。
5. 如果存在多个相同长度的 LIS，返回任意一个有效的 LIS 均可。

## 示例输入与输出

### 示例输入 1

```
DPLongestIncreasingSubsequence([]int{10, 9, 2, 5, 3, 7, 101, 18})
```

### 示例输出 1

```
4
```

### 示例输入 2

```
OptimizedLIS([]int{0, 1, 0, 3, 2, 3})
```

### 示例输出 2

```
4
```

### 示例输入 3

```
GetLISElements([]int{10, 9, 2, 5, 3, 7, 101, 18})
```

### 示例输出 3

```
[2, 5, 7, 101]
```
注意：[2, 3, 7, 18] 或 [2, 3, 7, 101] 也是有效输出，因为它们同样是有效的 LIS。

### 示例输入 4

```
DPLongestIncreasingSubsequence([]int{7, 7, 7, 7, 7, 7, 7})
```

### 示例输出 4

```
1
```

## 指令

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-24/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- 实现所需的函数。
- 通过运行测试文件在本地测试你的解决方案。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-24/` 目录下运行以下命令：

```bash
go test -v
```

## 性能预期

- **DPLongestIncreasingSubsequence**：时间复杂度 O(n²)，空间复杂度 O(n)。
- **OptimizedLIS**：时间复杂度 O(n log n)，空间复杂度 O(n)。
- **GetLISElements**：时间复杂度为 O(n²) 或 O(n log n)，具体取决于所采用的方法。