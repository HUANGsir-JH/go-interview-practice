# 挑战 27：Go 泛型数据结构提示

## 提示 1：泛型对偶实现
从一个简单的泛型对偶类型开始：
```go
// Pair 表示两个可能不同类型的值的泛型对偶
type Pair[T, U any] struct {
    First  T
    Second U
}

// NewPair 使用给定的值创建一个新的对偶
func NewPair[T, U any](first T, second U) Pair[T, U] {
    return Pair[T, U]{
        First:  first,
        Second: second,
    }
}

// Swap 返回一个元素互换的新对偶
func (p Pair[T, U]) Swap() Pair[U, T] {
    return Pair[U, T]{
        First:  p.Second,
        Second: p.First,
    }
}
```

## 提示 2：泛型栈实现
使用带有泛型类型参数的切片来实现栈：
```go
// Stack 是一个泛型的后进先出（LIFO）数据结构
type Stack[T any] struct {
    items []T
}

// NewStack 创建一个新空栈
func NewStack[T any]() *Stack[T] {
    return &Stack[T]{
        items: make([]T, 0),
    }
}

// Push 将元素添加到栈顶
func (s *Stack[T]) Push(value T) {
    s.items = append(s.items, value)
}

// Pop 移除并返回栈顶元素
func (s *Stack[T]) Pop() (T, error) {
    var zero T
    if len(s.items) == 0 {
        return zero, errors.New("栈为空")
    }
    
    index := len(s.items) - 1
    item := s.items[index]
    s.items = s.items[:index]
    return item, nil
}

// Peek 返回栈顶元素但不移除它
func (s *Stack[T]) Peek() (T, error) {
    var zero T
    if len(s.items) == 0 {
        return zero, errors.New("栈为空")
    }
    return s.items[len(s.items)-1], nil
}

// Size 返回栈中元素的数量
func (s *Stack[T]) Size() int {
    return len(s.items)
}

// IsEmpty 如果栈中没有元素则返回 true
func (s *Stack[T]) IsEmpty() bool {
    return len(s.items) == 0
}
```

## 提示 3：泛型队列实现
使用切片实现先进先出（FIFO）操作的队列：
```go
// Queue 是一个泛型的先进先出（FIFO）数据结构
type Queue[T any] struct {
    items []T
}

// NewQueue 创建一个新空队列
func NewQueue[T any]() *Queue[T] {
    return &Queue[T]{
        items: make([]T, 0),
    }
}

// Enqueue 将元素添加到队列末尾
func (q *Queue[T]) Enqueue(value T) {
    q.items = append(q.items, value)
}

// Dequeue 移除并返回队列前端元素
func (q *Queue[T]) Dequeue() (T, error) {
    var zero T
    if len(q.items) == 0 {
        return zero, errors.New("队列为空")
    }
    
    item := q.items[0]
    q.items = q.items[1:]
    return item, nil
}

// Front 返回前端元素但不移除它
func (q *Queue[T]) Front() (T, error) {
    var zero T
    if len(q.items) == 0 {
        return zero, errors.New("队列为空")
    }
    return q.items[0], nil
}

// Size 返回队列中元素的数量
func (q *Queue[T]) Size() int {
    return len(q.items)
}

// IsEmpty 如果队列中没有元素则返回 true
func (q *Queue[T]) IsEmpty() bool {
    return len(q.items) == 0
}
```

## 提示 4：带可比较约束的泛型集合实现
使用 map 实现高效的集合操作，使用可比较约束：
```go
// Set 是一个泛型的唯一元素集合
type Set[T comparable] struct {
    items map[T]struct{}
}

// NewSet 创建一个新空集合
func NewSet[T comparable]() *Set[T] {
    return &Set[T]{
        items: make(map[T]struct{}),
    }
}

// Add 添加元素到集合中，如果该元素尚未存在
func (s *Set[T]) Add(value T) {
    s.items[value] = struct{}{}
}

// Remove 从集合中移除元素（如果存在）
func (s *Set[T]) Remove(value T) {
    delete(s.items, value)
}

// Contains 如果集合包含给定元素则返回 true
func (s *Set[T]) Contains(value T) bool {
    _, exists := s.items[value]
    return exists
}

// Size 返回集合中元素的数量
func (s *Set[T]) Size() int {
    return len(s.items)
}

// Elements 返回包含集合中所有元素的切片
func (s *Set[T]) Elements() []T {
    elements := make([]T, 0, len(s.items))
    for item := range s.items {
        elements = append(elements, item)
    }
    return elements
}
```

## 提示 5：集合操作——并集、交集、差集
将集合操作实现为独立的泛型函数：
```go
// Union 返回一个新集合，包含两个集合中的所有元素
func Union[T comparable](s1, s2 *Set[T]) *Set[T] {
    result := NewSet[T]()
    
    // 添加 s1 中的所有元素
    for item := range s1.items {
        result.Add(item)
    }
    
    // 添加 s2 中的所有元素
    for item := range s2.items {
        result.Add(item)
    }
    
    return result
}

// Intersection 返回一个新集合，仅包含同时存在于两个集合中的元素
func Intersection[T comparable](s1, s2 *Set[T]) *Set[T] {
    result := NewSet[T]()
    
    // 为了效率，遍历较小的集合
    smaller, larger := s1, s2
    if s2.Size() < s1.Size() {
        smaller, larger = s2, s1
    }
    
    for item := range smaller.items {
        if larger.Contains(item) {
            result.Add(item)
        }
    }
    
    return result
}

// Difference 返回一个新集合，包含在 s1 中但不在 s2 中的元素
func Difference[T comparable](s1, s2 *Set[T]) *Set[T] {
    result := NewSet[T]()
    
    for item := range s1.items {
        if !s2.Contains(item) {
            result.Add(item)
        }
    }
    
    return result
}
```

## 提示 6：泛型实用函数——过滤、映射、归约
使用泛型实现函数式编程工具：
```go
// Filter 返回一个新切片，仅包含使谓词返回 true 的元素
func Filter[T any](slice []T, predicate func(T) bool) []T {
    result := make([]T, 0)
    for _, item := range slice {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

// Map 对切片中的每个元素应用函数，并返回结果的新切片
func Map[T, U any](slice []T, mapper func(T) U) []U {
    result := make([]U, len(slice))
    for i, item := range slice {
        result[i] = mapper(item)
    }
    return result
}

// Reduce 通过将函数应用于每个元素，将切片缩减为单个值
func Reduce[T, U any](slice []T, initial U, reducer func(U, T) U) U {
    result := initial
    for _, item := range slice {
        result = reducer(result, item)
    }
    return result
}
```

## 提示 7：附加实用函数
实现更多带泛型的切片工具：
```go
// Contains 如果切片包含给定元素则返回 true
func Contains[T comparable](slice []T, element T) bool {
    for _, item := range slice {
        if item == element {
            return true
        }
    }
    return false
}

// FindIndex 返回给定元素首次出现的索引，若未找到则返回 -1
func FindIndex[T comparable](slice []T, element T) int {
    for i, item := range slice {
        if item == element {
            return i
        }
    }
    return -1
}

// RemoveDuplicates 返回一个去重后的新切片，保持原有顺序
func RemoveDuplicates[T comparable](slice []T) []T {
    seen := make(map[T]struct{})
    result := make([]T, 0)
    
    for _, item := range slice {
        if _, exists := seen[item]; !exists {
            seen[item] = struct{}{}
            result = append(result, item)
        }
    }
    
    return result
}

// Reverse 返回一个元素顺序相反的新切片
func Reverse[T any](slice []T) []T {
    result := make([]T, len(slice))
    for i, item := range slice {
        result[len(slice)-1-i] = item
    }
    return result
}
```

## Go 泛型核心概念：
- **类型参数**：使用 `[T any]` 定义泛型类型和函数
- **类型约束**：使用 `comparable` 约束进行相等性操作
- **类型推断**：Go 通常能根据使用情况推断泛型类型
- **零值**：使用 `var zero T` 获取泛型类型的零值
- **多个类型参数**：函数可以有多个泛型类型，如 `[T, U any]`
- **方法集**：泛型类型可以拥有带类型参数的方法