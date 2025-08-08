[查看排行榜](SCOREBOARD.md)

# 挑战 21：二分查找实现

## 问题描述

实现二分查找算法，以高效地在有序集合中查找元素。二分查找是一种分治算法，通过反复将搜索空间一分为二，使得其在有序数据上的查找速度远快于线性查找。

你需要实现二分查找的三种版本：

1. `BinarySearch` - 标准二分查找，返回目标值的索引。
2. `BinarySearchRecursive` - 二分查找的递归实现。
3. `FindInsertPosition` - 找到插入值的位置以保持有序顺序。

## 函数签名

```go
func BinarySearch(arr []int, target int) int
func BinarySearchRecursive(arr []int, target int, left int, right int) int
func FindInsertPosition(arr []int, target int) int
```

## 输入格式

- 对所有函数，输入为一个整数切片 `arr`（已排序）和一个目标整数值。
- 对于递归函数，额外提供 `left` 和 `right` 参数，表示搜索范围。

## 输出格式

- `BinarySearch` 和 `BinarySearchRecursive` 应返回目标值的索引（若找到），否则返回 -1。
- `FindInsertPosition` 应返回目标值应插入的位置，以保持数组有序。

## 要求

1. 所有函数必须实现二分查找算法，时间复杂度为 O(log n)。
2. 假设数组按升序排列。
3. `BinarySearchRecursive` 必须使用递归来解决问题。
4. 如果目标值存在多个重复项，返回任意一个位置的索引即可。

## 示例输入与输出

### 示例输入 1

```
BinarySearch([]int{1, 3, 5, 7, 9}, 5)
```

### 示例输出 1

```
2
```

### 示例输入 2

```
BinarySearch([]int{1, 3, 5, 7, 9}, 6)
```

### 示例输出 2

```
-1
```

### 示例输入 3

```
BinarySearchRecursive([]int{1, 3, 5, 7, 9}, 7, 0, 4)
```

### 示例输出 3

```
3
```

### 示例输入 4

```
FindInsertPosition([]int{1, 3, 5, 7, 9}, 6)
```

### 示例输出 4

```
3
```

## 指导说明

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-21/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的函数。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-21/` 目录下运行以下命令：

```bash
go test -v
```