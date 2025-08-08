# 挑战 27：Go 泛型数据结构

## 问题描述

在此挑战中，你将使用 Go 实现一组泛型数据结构和算法。这将帮助你练习使用 Go 的泛型功能（自 Go 1.18 引入）来创建可重用且类型安全的代码。

你的任务是实现几种可以与任何合适类型一起工作的泛型数据结构：

1. 一个可以容纳不同类型两个值的泛型 `Pair[T, U]` 类型
2. 具有标准栈操作的泛型 `Stack[T]` 数据结构
3. 具有标准队列操作的泛型 `Queue[T]` 数据结构
4. 具有基本集合操作的泛型 `Set[T]` 数据结构
5. 一组用于处理切片的泛型实用函数

这些实现将展示如何使用 Go 的泛型来创建灵活且类型安全的代码。

## 函数签名

### 1. 泛型 Pair

```go
// Pair 表示一对可能不同类型的值
type Pair[T, U any] struct {
    First  T
    Second U
}

// NewPair 使用给定的值创建一个新的配对
func NewPair[T, U any](first T, second U) Pair[T, U]

// Swap 返回一个元素交换顺序的新配对
func (p Pair[T, U]) Swap() Pair[U, T]
```

### 2. 泛型 Stack

```go
// Stack 是一个泛型后进先出（LIFO）数据结构
type Stack[T any] struct {
    // 私有实现细节
}

// NewStack 创建一个新的空栈
func NewStack[T any]() *Stack[T]

// Push 将元素添加到栈顶
func (s *Stack[T]) Push(value T)

// Pop 移除并返回栈顶元素
// 如果栈为空，则返回错误
func (s *Stack[T]) Pop() (T, error)

// Peek 返回栈顶元素但不移除它
// 如果栈为空，则返回错误
func (s *Stack[T]) Peek() (T, error)

// Size 返回栈中的元素数量
func (s *Stack[T]) Size() int

// IsEmpty 如果栈中没有元素则返回 true
func (s *Stack[T]) IsEmpty() bool
```

### 3. 泛型 Queue

```go
// Queue 是一个泛型先进先出（FIFO）数据结构
type Queue[T any] struct {
    // 私有实现细节
}

// NewQueue 创建一个新的空队列
func NewQueue[T any]() *Queue[T]

// Enqueue 将元素添加到队列末尾
func (q *Queue[T]) Enqueue(value T)

// Dequeue 移除并返回队列前端的元素
// 如果队列为空，则返回错误
func (q *Queue[T]) Dequeue() (T, error)

// Front 返回前端元素但不移除它
// 如果队列为空，则返回错误
func (q *Queue[T]) Front() (T, error)

// Size 返回队列中的元素数量
func (q *Queue[T]) Size() int

// IsEmpty 如果队列中没有元素则返回 true
func (q *Queue[T]) IsEmpty() bool
```

### 4. 泛型 Set

```go
// Set 是一个包含唯一元素的泛型集合
type Set[T comparable] struct {
    // 私有实现细节
}

// NewSet 创建一个新的空集合
func NewSet[T comparable]() *Set[T]

// Add 如果元素尚未存在，则将其添加到集合中
func (s *Set[T]) Add(value T)

// Remove 如果元素存在，则将其从集合中移除
func (s *Set[T]) Remove(value T)

// Contains 如果集合包含给定元素则返回 true
func (s *Set[T]) Contains(value T) bool

// Size 返回集合中的元素数量
func (s *Set[T]) Size() int

// Elements 返回包含集合中所有元素的切片
func (s *Set[T]) Elements() []T

// Union 返回一个新集合，包含两个集合的所有元素
func Union[T comparable](s1, s2 *Set[T]) *Set[T]

// Intersection 返回一个新集合，仅包含同时存在于两个集合中的元素
func Intersection[T comparable](s1, s2 *Set[T]) *Set[T]

// Difference 返回一个新集合，包含在 s1 中但不在 s2 中的元素
func Difference[T comparable](s1, s2 *Set[T]) *Set[T]
```

### 5. 泛型实用函数

```go
// Filter 返回一个新切片，其中只包含使谓词返回 true 的元素
func Filter[T any](slice []T, predicate func(T) bool) []T

// Map 对切片中的每个元素应用一个函数，并返回结果组成的新切片
func Map[T, U any](slice []T, mapper func(T) U) []U

// Reduce 通过将函数应用于每个元素，将切片缩减为单个值
func Reduce[T, U any](slice []T, initial U, reducer func(U, T) U) U

// Contains 如果切片包含给定元素则返回 true
func Contains[T comparable](slice []T, element T) bool

// FindIndex 返回第一个出现给定元素的索引，如果未找到则返回 -1
func FindIndex[T comparable](slice []T, element T) int

// RemoveDuplicates 返回一个去除重复元素的新切片，保持原有顺序
func RemoveDuplicates[T comparable](slice []T) []T
```

## 输入/输出示例

### Pair 示例
```go
// 创建一个配对
p := NewPair("answer", 42)
fmt.Println(p.First)  // "answer"
fmt.Println(p.Second) // 42

// 交换
swapped := p.Swap()
fmt.Println(swapped.First)  // 42
fmt.Println(swapped.Second) // "answer"
```

### Stack 示例
```go
// 创建一个整数栈
stack := NewStack[int]()
stack.Push(1)
stack.Push(2)
stack.Push(3)

val, err := stack.Peek()
// val == 3, err == nil

val, err = stack.Pop()
// val == 3, err == nil

val, err = stack.Pop()
// val == 2, err == nil

size := stack.Size()
// size == 1

isEmpty := stack.IsEmpty()
// isEmpty == false
```

### Queue 示例
```go
// 创建一个字符串队列
queue := NewQueue[string]()
queue.Enqueue("first")
queue.Enqueue("second")
queue.Enqueue("third")

val, err := queue.Front()
// val == "first", err == nil

val, err = queue.Dequeue()
// val == "first", err == nil

val, err = queue.Dequeue()
// val == "second", err == nil

size := queue.Size()
// size == 1

isEmpty := queue.IsEmpty()
// isEmpty == false
```

### Set 示例
```go
// 创建整数集合
set1 := NewSet[int]()
set1.Add(1)
set1.Add(2)
set1.Add(3)
set1.Add(2) // 重复项，不会被添加

set2 := NewSet[int]()
set2.Add(2)
set2.Add(3)
set2.Add(4)

contains := set1.Contains(2)
// contains == true

union := Union(set1, set2)
// union 包含 1, 2, 3, 4

intersection := Intersection(set1, set2)
// intersection 包含 2, 3

difference := Difference(set1, set2)
// difference 包含 1
```

### 实用函数示例
```go
// Filter
numbers := []int{1, 2, 3, 4, 5, 6}
evens := Filter(numbers, func(n int) bool {
    return n%2 == 0
})
// evens == [2, 4, 6]

// Map
squares := Map(numbers, func(n int) int {
    return n * n
})
// squares == [1, 4, 9, 16, 25, 36]

// Reduce
sum := Reduce(numbers, 0, func(acc, n int) int {
    return acc + n
})
// sum == 21

// Contains
hasThree := Contains(numbers, 3)
// hasThree == true

// FindIndex
index := FindIndex(numbers, 4)
// index == 3

// RemoveDuplicates
withDuplicates := []int{1, 2, 2, 3, 1, 4, 5, 5}
uniques := RemoveDuplicates(withDuplicates)
// uniques == [1, 2, 3, 4, 5]
```

## 约束条件

- 你的实现必须正确使用 Go 的泛型特性
- 所有函数必须具有适当的类型约束
- 实现在时间和空间复杂度上应高效
- 必须适当处理边界情况（如空集合等）
- 你的代码应能使用 Go 1.18 或更高版本编译通过

## 评估标准

- 正确性：你的解决方案是否正确实现了所有要求的数据结构和函数？
- 泛型的恰当使用：你是否有效使用了泛型，并设置了合适的类型约束？
- 代码质量：你的代码是否结构良好、清晰易读且易于维护？
- 性能：你的实现是否在时间和空间复杂度上高效？
- 错误处理：你的代码是否能优雅地处理错误情况？

## 学习资源

参见 [learning.md](learning.md) 文件以获取关于在 Go 中使用泛型的全面指南。

## 提示

1. 请记住，用于作为 map 键或使用 `==` 和 `!=` 进行比较的类型需要 `comparable` 约束
2. 对于可能失败的操作（如从空栈弹出），应同时返回零值和错误
3. `any` 约束表示允许任何类型，但更具体的约束可提供更好的类型安全性
4. 在许多情况下类型参数可以推断出来，但在某些情境下显式类型参数可提高清晰度
5. Go 的泛型实现设计简洁且性能优异——专注于编写干净、符合习惯的代码，而非复杂的类型操作