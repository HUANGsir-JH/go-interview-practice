# Go 泛型学习资料

## Go 中的泛型简介

Go 1.18 引入了对泛型编程的支持，使开发者能够编写可处理多种类型但保持类型安全的代码。此功能在不牺牲编译时类型检查的前提下，实现了更灵活和可重用的代码。

### 为什么需要泛型？

在泛型出现之前，Go 开发者有几种处理多类型的方法：

1. **interface{}**：使用空接口可以接受任何类型，但需要类型断言，并且失去了编译时类型检查。
2. **代码生成**：像 `go generate` 这样的工具可以创建特定类型的实现，但这增加了构建过程的复杂性。
3. **复制粘贴**：为不同类型重复编写代码会导致维护困难。

泛型通过提供一种既能保证类型安全又能跨多种类型重用代码的方式解决了这些问题。

### 基本语法

在 Go 中定义泛型函数的基本语法如下：

```go
func MyGenericFunction[T any](param T) T {
    // 函数体
    return param
}
```

以及泛型类型的定义：

```go
type MyGenericType[T any] struct {
    Value T
}
```

### 类型参数与约束

类型参数用方括号 `[T any]` 指定，其中：
- `T` 是类型参数名称
- `any` 是类型约束（此处表示允许任意类型）

Go 在 `constraints` 包中提供了多个预定义的约束：

```go
import "golang.org/x/exp/constraints"

// 适用于任何有序类型的函数
func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

### 自定义类型约束

你可以使用接口类型来定义自定义约束：

```go
// 定义一个要求具有 String() 方法的约束
type Stringer interface {
    String() string
}

// 适用于任何实现 String() 的类型的函数
func PrintValue[T Stringer](value T) {
    fmt.Println(value.String())
}
```

### 约束中的联合类型

Go 泛型支持约束中的联合类型，允许参数接受多个特定类型：

```go
// 接受 int 或 float64 的约束
type Number interface {
    int | float64
}

// 适用于 int 或 float64 的函数
func Add[T Number](a, b T) T {
    return a + b
}
```

### 类型集合

类型集合是 Go 泛型实现的核心概念。一个约束定义了一组满足该约束的类型：

```go
// 支持 == 和 != 比较的类型约束
type Comparable[T any] interface {
    comparable
}

// 检查两个值是否相等的函数
func AreEqual[T comparable](a, b T) bool {
    return a == b
}
```

### 泛型数据结构

泛型特别适用于实现数据结构：

```go
// 泛型栈实现
type Stack[T any] struct {
    elements []T
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{elements: make([]T, 0)}
}

func (s *Stack[T]) Push(element T) {
    s.elements = append(s.elements, element)
}

func (s *Stack[T]) Pop() (T, error) {
    var zero T
    if len(s.elements) == 0 {
        return zero, errors.New("栈为空")
    }
    
    lastIndex := len(s.elements) - 1
    element := s.elements[lastIndex]
    s.elements = s.elements[:lastIndex]
    return element, nil
}

func (s *Stack[T]) Peek() (T, error) {
    var zero T
    if len(s.elements) == 0 {
        return zero, errors.New("栈为空")
    }
    
    return s.elements[len(s.elements)-1], nil
}

func (s *Stack[T]) Size() int {
    return len(s.elements)
}

func (s *Stack[T]) IsEmpty() bool {
    return len(s.elements) == 0
}
```

### 类型推断

Go 通常可以根据参数推断出类型参数：

```go
func Identity[T any](value T) T {
    return value
}

// 类型推断示例
str := Identity("hello")    // T 被推断为 string
num := Identity(42)         // T 被推断为 int
```

### 多个类型参数

函数和类型可以拥有多个类型参数：

```go
// 将一种类型的切片转换为另一种类型的映射函数
func Map[T, U any](slice []T, f func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = f(v)
    }
    return result
}

// 使用示例
numbers := []int{1, 2, 3, 4}
squares := Map(numbers, func(x int) int { return x * x })
// squares: [1, 4, 9, 16]

// 将数字转换为字符串
strNumbers := Map(numbers, func(x int) string { return strconv.Itoa(x) })
// strNumbers: ["1", "2", "3", "4"]
```

### 泛型与方法结合

可以在泛型类型上定义方法：

```go
type Pair[T, U any] struct {
    First  T
    Second U
}

func (p Pair[T, U]) Swap() Pair[U, T] {
    return Pair[U, T]{First: p.Second, Second: p.First}
}

// 使用示例
pair := Pair[string, int]{First: "answer", Second: 42}
swapped := pair.Swap() // Pair[int, string]{First: 42, Second: "answer"}
```

### 约束包

`golang.org/x/exp/constraints` 包提供了有用的约束：

```go
import "golang.org/x/exp/constraints"

// 适用于任何整数类型的函数
func Sum[T constraints.Integer](values []T) T {
    var sum T
    for _, v := range values {
        sum += v
    }
    return sum
}

// 适用于任何浮点类型的函数
func Average[T constraints.Float](values []T) T {
    sum := T(0)
    for _, v := range values {
        sum += v
    }
    return sum / T(len(values))
}
```

主要约束包括：
- `Integer`：任意整数类型
- `Float`：任意浮点类型
- `Complex`：任意复数类型
- `Ordered`：支持 `<` 操作符的任意类型
- `Signed`：任意有符号整数类型
- `Unsigned`：任意无符号整数类型

### 泛型算法

泛型非常适合实现适用于多种类型的算法：

```go
// 泛型二分查找函数
func BinarySearch[T constraints.Ordered](slice []T, target T) int {
    left, right := 0, len(slice)-1
    
    for left <= right {
        mid := (left + right) / 2
        
        if slice[mid] == target {
            return mid
        } else if slice[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    
    return -1 // 未找到
}
```

### 方法中的类型参数

方法本身不能拥有独立于接收者类型的类型参数，但可以通过泛型函数绕过这一限制：

```go
// 这将无法编译——方法不能有自己的类型参数
// func (s *Stack[T]) ConvertTo[U any](converter func(T) U) []U { ... }

// 取而代之的是使用普通函数
func ConvertStack[T, U any](stack *Stack[T], converter func(T) U) []U {
    result := make([]U, stack.Size())
    for i, v := range stack.elements {
        result[i] = converter(v)
    }
    return result
}
```

### 零值与泛型类型

在使用泛型时，通常需要生成类型参数的“零值”：

```go
func GetZero[T any]() T {
    var zero T
    return zero
}

// 使用示例
zeroInt := GetZero[int]()       // 0
zeroString := GetZero[string]() // ""
```

### 性能考虑

Go 中的泛型在实现时充分考虑了性能：

1. **编译方式**：Go 采用混合策略，在每个类型实例化时生成特定代码的同时尽可能共享代码。
2. **运行时效率**：泛型代码在编译时被优化，因此与手动编写的特定类型代码相比，运行时开销极小。
3. **代码大小**：使用大量类型实例化可能会增加二进制文件大小，但编译器会尽量减小这种影响。

### 使用泛型的最佳实践

1. **避免过度使用泛型**：只有当泛型在代码重用和类型安全方面带来明显优势时才使用。
2. **约束要具体**：根据使用场景尽可能使用最具体的约束。
3. **提供清晰文档**：清楚地记录泛型函数和类型的预期行为。
4. **考虑性能影响**：注意泛型对编译时间和二进制大小的影响。

### 实际应用示例

#### 泛型结果类型

一种常见模式是创建一个泛型结果类型以处理成功和错误情况：

```go
type Result[T any] struct {
    Value T
    Error error
}

func NewSuccess[T any](value T) Result[T] {
    return Result[T]{Value: value, Error: nil}
}

func NewError[T any](err error) Result[T] {
    var zero T
    return Result[T]{Value: zero, Error: err}
}

// 使用示例
func DivideInts(a, b int) Result[int] {
    if b == 0 {
        return NewError[int](errors.New("除零错误"))
    }
    return NewSuccess(a / b)
}
```

#### 泛型集合实现

```go
type Set[T comparable] struct {
    elements map[T]struct{}
}

func NewSet[T comparable]() Set[T] {
    return Set[T]{elements: make(map[T]struct{})}
}

func (s *Set[T]) Add(element T) {
    s.elements[element] = struct{}{}
}

func (s *Set[T]) Remove(element T) {
    delete(s.elements, element)
}

func (s *Set[T]) Contains(element T) bool {
    _, exists := s.elements[element]
    return exists
}

func (s *Set[T]) Size() int {
    return len(s.elements)
}

func (s *Set[T]) Elements() []T {
    result := make([]T, 0, len(s.elements))
    for element := range s.elements {
        result = append(result, element)
    }
    return result
}

// 集合操作
func Union[T comparable](s1, s2 Set[T]) Set[T] {
    result := NewSet[T]()
    
    for element := range s1.elements {
        result.Add(element)
    }
    
    for element := range s2.elements {
        result.Add(element)
    }
    
    return result
}

func Intersection[T comparable](s1, s2 Set[T]) Set[T] {
    result := NewSet[T]()
    
    for element := range s1.elements {
        if s2.Contains(element) {
            result.Add(element)
        }
    }
    
    return result
}
```

### 进一步阅读

1. [Go 泛型设计文档](https://go.googlesource.com/proposal/+/refs/heads/master/design/43651-type-parameters.md)
2. [Go by Example: 泛型](https://gobyexample.com/generics)
3. [Go 泛型入门](https://go101.org/generics/101.html)
4. [《Go 编程语言》博客：在 Go 中使用泛型](https://go.dev/blog/intro-generics)
5. [Go 泛型实战](https://bitfieldconsulting.com/golang/generics)