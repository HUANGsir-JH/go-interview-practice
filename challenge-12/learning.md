# 通用数据结构学习材料

## Go 中的泛型

Go 1.18 引入了泛型，允许进行类型参数化编程，这使得可以编写适用于不同类型的函数和数据结构，同时保持类型安全。本挑战聚焦于实现泛型数据结构。

### 泛型简介

泛型允许您编写在多种类型上操作的代码，同时保持类型安全：

```go
// 泛型之前：每种类型都需要单独的函数
func SumInts(numbers []int) int {
    sum := 0
    for _, n := range numbers {
        sum += n
    }
    return sum
}

func SumFloats(numbers []float64) float64 {
    sum := 0.0
    for _, n := range numbers {
        sum += n
    }
    return sum
}

// 使用泛型：一个函数适用于多种类型
func Sum[T constraints.Ordered](numbers []T) T {
    var sum T
    for _, n := range numbers {
        sum += n
    }
    return sum
}

// 使用示例
intSum := Sum([]int{1, 2, 3})               // 6
floatSum := Sum([]float64{1.1, 2.2, 3.3})   // 6.6
```

### 类型参数与约束

类型参数允许函数和类型处理不同的类型：

```go
// T 是一个类型参数
// constraints.Ordered 是 T 必须满足的约束
func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

约束指定了可以在类型参数上执行的操作：

```go
// 自定义约束：支持加法的类型
type Addable interface {
    int | int64 | float64 | string
}

// 使用自定义约束的函数
func Add[T Addable](a, b T) T {
    return a + b
}
```

### `constraints` 包

Go 标准库在 `constraints` 包中提供了常见的约束：

```go
import "golang.org/x/exp/constraints"

// 预定义约束示例
// constraints.Ordered: 支持 < <= >= > 的类型
// constraints.Integer: 整数类型
// constraints.Float: 浮点数类型
// constraints.Complex: 复数类型
```

### 泛型数据结构

泛型使创建可重用的数据结构成为可能：

#### 泛型栈

```go
// 泛型栈
type Stack[T any] struct {
    elements []T
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{elements: make([]T, 0)}
}

func (s *Stack[T]) Push(element T) {
    s.elements = append(s.elements, element)
}

func (s *Stack[T]) Pop() (T, bool) {
    var zero T
    if len(s.elements) == 0 {
        return zero, false
    }
    
    lastIndex := len(s.elements) - 1
    element := s.elements[lastIndex]
    s.elements = s.elements[:lastIndex]
    return element, true
}

func (s *Stack[T]) Peek() (T, bool) {
    var zero T
    if len(s.elements) == 0 {
        return zero, false
    }
    
    return s.elements[len(s.elements)-1], true
}

func (s *Stack[T]) IsEmpty() bool {
    return len(s.elements) == 0
}

func (s *Stack[T]) Size() int {
    return len(s.elements)
}
```

#### 泛型队列

```go
// 泛型队列
type Queue[T any] struct {
    elements []T
}

func NewQueue[T any]() *Queue[T] {
    return &Queue[T]{elements: make([]T, 0)}
}

func (q *Queue[T]) Enqueue(element T) {
    q.elements = append(q.elements, element)
}

func (q *Queue[T]) Dequeue() (T, bool) {
    var zero T
    if len(q.elements) == 0 {
        return zero, false
    }
    
    element := q.elements[0]
    q.elements = q.elements[1:]
    return element, true
}

func (q *Queue[T]) Peek() (T, bool) {
    var zero T
    if len(q.elements) == 0 {
        return zero, false
    }
    
    return q.elements[0], true
}

func (q *Queue[T]) IsEmpty() bool {
    return len(q.elements) == 0
}

func (q *Queue[T]) Size() int {
    return len(q.elements)
}
```

#### 泛型链表

```go
// 泛型链表节点
type Node[T any] struct {
    Value T
    Next  *Node[T]
}

// 泛型链表
type LinkedList[T any] struct {
    head *Node[T]
    tail *Node[T]
    size int
}

func NewLinkedList[T any]() *LinkedList[T] {
    return &LinkedList[T]{}
}

func (l *LinkedList[T]) Append(value T) {
    node := &Node[T]{Value: value}
    
    if l.head == nil {
        l.head = node
        l.tail = node
    } else {
        l.tail.Next = node
        l.tail = node
    }
    
    l.size++
}

func (l *LinkedList[T]) Prepend(value T) {
    node := &Node[T]{Value: value, Next: l.head}
    
    if l.head == nil {
        l.tail = node
    }
    
    l.head = node
    l.size++
}

func (l *LinkedList[T]) Remove(value T, equals func(a, b T) bool) bool {
    if l.head == nil {
        return false
    }
    
    // 特殊情况：移除头节点
    if equals(l.head.Value, value) {
        l.head = l.head.Next
        l.size--
        
        if l.head == nil {
            l.tail = nil
        }
        
        return true
    }
    
    // 找到要移除节点的前一个节点
    current := l.head
    for current.Next != nil && !equals(current.Next.Value, value) {
        current = current.Next
    }
    
    // 如果找到，则移除它
    if current.Next != nil {
        if current.Next == l.tail {
            l.tail = current
        }
        
        current.Next = current.Next.Next
        l.size--
        return true
    }
    
    return false
}

func (l *LinkedList[T]) Contains(value T, equals func(a, b T) bool) bool {
    current := l.head
    
    for current != nil {
        if equals(current.Value, value) {
            return true
        }
        current = current.Next
    }
    
    return false
}

func (l *LinkedList[T]) Size() int {
    return l.size
}

func (l *LinkedList[T]) IsEmpty() bool {
    return l.size == 0
}

func (l *LinkedList[T]) ToSlice() []T {
    result := make([]T, l.size)
    current := l.head
    i := 0
    
    for current != nil {
        result[i] = current.Value
        current = current.Next
        i++
    }
    
    return result
}
```

#### 泛型二叉搜索树

```go
// 泛型二叉搜索树节点
type TreeNode[T constraints.Ordered] struct {
    Value T
    Left  *TreeNode[T]
    Right *TreeNode[T]
}

// 泛型二叉搜索树
type BinarySearchTree[T constraints.Ordered] struct {
    root *TreeNode[T]
    size int
}

func NewBinarySearchTree[T constraints.Ordered]() *BinarySearchTree[T] {
    return &BinarySearchTree[T]{}
}

func (t *BinarySearchTree[T]) Insert(value T) {
    t.root = t.insertHelper(t.root, value)
    t.size++
}

func (t *BinarySearchTree[T]) insertHelper(node *TreeNode[T], value T) *TreeNode[T] {
    if node == nil {
        return &TreeNode[T]{Value: value}
    }
    
    if value < node.Value {
        node.Left = t.insertHelper(node.Left, value)
    } else {
        node.Right = t.insertHelper(node.Right, value)
    }
    
    return node
}

func (t *BinarySearchTree[T]) Contains(value T) bool {
    return t.containsHelper(t.root, value)
}

func (t *BinarySearchTree[T]) containsHelper(node *TreeNode[T], value T) bool {
    if node == nil {
        return false
    }
    
    if value == node.Value {
        return true
    }
    
    if value < node.Value {
        return t.containsHelper(node.Left, value)
    }
    
    return t.containsHelper(node.Right, value)
}

func (t *BinarySearchTree[T]) InOrderTraversal() []T {
    result := make([]T, 0, t.size)
    t.inOrderHelper(t.root, &result)
    return result
}

func (t *BinarySearchTree[T]) inOrderHelper(node *TreeNode[T], result *[]T) {
    if node == nil {
        return
    }
    
    t.inOrderHelper(node.Left, result)
    *result = append(*result, node.Value)
    t.inOrderHelper(node.Right, result)
}

func (t *BinarySearchTree[T]) Size() int {
    return t.size
}

func (t *BinarySearchTree[T]) IsEmpty() bool {
    return t.size == 0
}
```

#### 泛型映射

```go
// 泛型映射（需要键的哈希函数）
type Map[K comparable, V any] struct {
    data map[K]V
}

func NewMap[K comparable, V any]() *Map[K, V] {
    return &Map[K, V]{
        data: make(map[K]V),
    }
}

func (m *Map[K, V]) Put(key K, value V) {
    m.data[key] = value
}

func (m *Map[K, V]) Get(key K) (V, bool) {
    value, ok := m.data[key]
    return value, ok
}

func (m *Map[K, V]) Remove(key K) {
    delete(m.data, key)
}

func (m *Map[K, V]) Contains(key K) bool {
    _, ok := m.data[key]
    return ok
}

func (m *Map[K, V]) Keys() []K {
    keys := make([]K, 0, len(m.data))
    for k := range m.data {
        keys = append(keys, k)
    }
    return keys
}

func (m *Map[K, V]) Values() []V {
    values := make([]V, 0, len(m.data))
    for _, v := range m.data {
        values = append(values, v)
    }
    return values
}

func (m *Map[K, V]) Size() int {
    return len(m.data)
}

func (m *Map[K, V]) IsEmpty() bool {
    return len(m.data) == 0
}
```

### 泛型算法

泛型允许实现适用于多种类型的算法：

#### 泛型二分查找

```go
// 在已排序切片上进行二分查找
func BinarySearch[T constraints.Ordered](slice []T, target T) (int, bool) {
    low, high := 0, len(slice)-1
    
    for low <= high {
        mid := (low + high) / 2
        
        if slice[mid] == target {
            return mid, true
        }
        
        if slice[mid] < target {
            low = mid + 1
        } else {
            high = mid - 1
        }
    }
    
    return -1, false
}
```

#### 泛型排序

```go
// 泛型冒泡排序
func BubbleSort[T constraints.Ordered](slice []T) {
    n := len(slice)
    for i := 0; i < n-1; i++ {
        for j := 0; j < n-i-1; j++ {
            if slice[j] > slice[j+1] {
                slice[j], slice[j+1] = slice[j+1], slice[j]
            }
        }
    }
}

// 使用自定义比较器
func BubbleSortFunc[T any](slice []T, less func(a, b T) bool) {
    n := len(slice)
    for i := 0; i < n-1; i++ {
        for j := 0; j < n-i-1; j++ {
            if less(slice[j+1], slice[j]) {
                slice[j], slice[j+1] = slice[j+1], slice[j]
            }
        }
    }
}
```

### 带方法的类型参数

方法也可以使用类型参数，但必须在结构体本身上声明，不能后期添加：

```go
// 这是可行的——在结构体上使用类型参数
type Pair[T any] struct {
    First, Second T
}

func (p *Pair[T]) Swap() {
    p.First, p.Second = p.Second, p.First
}

// 这不可行——无法添加带类型参数的方法
// func (p Pair) SwapAny[T any](pair Pair[T]) {
//     p.First, p.Second = pair.Second, pair.First
// }
```

### 设计泛型接口

泛型接口允许指定适用于不同类型的工作契约：

```go
// 泛型集合接口
type Collection[T any] interface {
    Add(item T)
    Remove(item T) bool
    Contains(item T) bool
    Size() int
    IsEmpty() bool
    Clear()
    ForEach(func(T))
}

// 实现接口
type ArrayList[T any] struct {
    items []T
    equals func(a, b T) bool
}

func NewArrayList[T any](equals func(a, b T) bool) *ArrayList[T] {
    return &ArrayList[T]{
        items: make([]T, 0),
        equals: equals,
    }
}

func (a *ArrayList[T]) Add(item T) {
    a.items = append(a.items, item)
}

func (a *ArrayList[T]) Remove(item T) bool {
    for i, val := range a.items {
        if a.equals(val, item) {
            a.items = append(a.items[:i], a.items[i+1:]...)
            return true
        }
    }
    return false
}

func (a *ArrayList[T]) Contains(item T) bool {
    for _, val := range a.items {
        if a.equals(val, item) {
            return true
        }
    }
    return false
}

func (a *ArrayList[T]) Size() int {
    return len(a.items)
}

func (a *ArrayList[T]) IsEmpty() bool {
    return len(a.items) == 0
}

func (a *ArrayList[T]) Clear() {
    a.items = make([]T, 0)
}

func (a *ArrayList[T]) ForEach(f func(T)) {
    for _, item := range a.items {
        f(item)
    }
}
```

### 泛型函数类型

函数也可以被参数化：

```go
// 泛型函数类型
type Transformer[T, U any] func(T) U

// 应用转换到每个元素的 Map 函数
func Map[T, U any](slice []T, transformer Transformer[T, U]) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = transformer(v)
    }
    return result
}

// 使用示例
numbers := []int{1, 2, 3, 4}
squares := Map(numbers, func(x int) int { return x * x })
// squares 是 [1, 4, 9, 16]
```

### 泛型的最佳实践

1. **使用泛型减少重复**：当您为不同类型编写相似函数时应用泛型
2. **选择适当的约束**：使用最严格但能满足需求的约束
3. **不要过度使用泛型**：只有当优势超过复杂性时才使用
4. **考虑性能影响**：泛型代码有时可能比特定类型代码慢
5. **提供具体类型的辅助函数**：为常见具体类型提供便捷函数

```go
// 字符串比较的辅助函数
func NewStringArrayList() *ArrayList[string] {
    return NewArrayList[string](func(a, b string) bool { return a == b })
}

// 整数比较的辅助函数
func NewIntArrayList() *ArrayList[int] {
    return NewArrayList[int](func(a, b int) bool { return a == b })
}
```

## 进一步阅读

- [Go 泛型教程](https://go.dev/doc/tutorial/generics)
- [在 Go 中使用泛型](https://pkg.go.dev/golang.org/x/exp@v0.0.0-20220613132600-b0d781184e0d/rand)
- [何时使用泛型](https://go.dev/blog/when-generics)
- [类型参数提案](https://go.googlesource.com/proposal/+/refs/heads/master/design/43651-type-parameters.md)