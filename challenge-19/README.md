[查看排行榜](SCOREBOARD.md)

# 挑战 19：切片操作

## 问题描述

编写函数以对切片（Go 的动态数组）执行常见操作。你需要实现以下函数：

1. `FindMax` - 在整数切片中查找最大值。
2. `RemoveDuplicates` - 移除切片中的重复值，同时保持顺序。
3. `ReverseSlice` - 反转切片中元素的顺序。
4. `FilterEven` - 创建一个新切片，仅包含原始切片中的偶数。

## 函数签名

```go
func FindMax(numbers []int) int
func RemoveDuplicates(numbers []int) []int
func ReverseSlice(slice []int) []int
func FilterEven(numbers []int) []int
```

## 输入格式

- 所有函数的输入均为整数切片。

## 输出格式

- `FindMax` - 一个表示最大值的整数。
- `RemoveDuplicates` - 移除重复项后的整数切片。
- `ReverseSlice` - 逆序排列的整数切片。
- `FilterEven` - 仅包含偶数的整数切片。

## 要求

1. `FindMax` 应返回切片中的最大值。如果切片为空，则返回 0。
2. `RemoveDuplicates` 应在移除重复项的同时保持元素的原始顺序。
3. `ReverseSlice` 应创建一个元素顺序相反的新切片。
4. `FilterEven` 应返回仅包含偶数的新切片。

## 示例输入与输出

### 示例输入 1

```
FindMax([]int{3, 1, 4, 1, 5, 9, 2, 6})
```

### 示例输出 1

```
9
```

### 示例输入 2

```
RemoveDuplicates([]int{3, 1, 4, 1, 5, 9, 2, 6})
```

### 示例输出 2

```
[3 1 4 5 9 2 6]
```

### 示例输入 3

```
ReverseSlice([]int{1, 2, 3, 4, 5})
```

### 示例输出 3

```
[5 4 3 2 1]
```

### 示例输入 4

```
FilterEven([]int{1, 2, 3, 4, 5, 6})
```

### 示例输出 4

```
[2 4 6]
```

## 指导说明

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-19/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的函数。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-19/` 目录中运行以下命令：

```bash
go test -v
```