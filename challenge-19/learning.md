# 切片操作学习资料

## 在 Go 中使用切片

切片是 Go 中最灵活且最常用的的数据结构之一。它们提供对底层数组的便捷视图，并在 Go 程序中被广泛使用。

### 切片基础

切片是对数组中连续段落的引用。与数组不同，切片的大小是动态的。

#### 创建切片

```go
// 使用字面量创建切片
numbers := []int{1, 2, 3, 4, 5}

// 使用 make 创建空切片
slice := make([]int, 5)      // 长度为 5，容量为 5 的切片
slice := make([]int, 0, 10)  // 长度为 0，容量为 10 的切片

// 从现有数组或切片创建切片
array := [5]int{1, 2, 3, 4, 5}
slice := array[1:4]  // [2, 3, 4]
```

#### 切片长度和容量

切片具有长度和容量：
- 长度：切片包含的元素数量（`len(slice)`）
- 容量：底层数组中的元素数量（`cap(slice)`）

```go
slice := make([]int, 3, 5)
fmt.Println(len(slice))  // 3
fmt.Println(cap(slice))  // 5
```

### 常见的切片操作

#### 向切片追加元素

`append` 函数将元素添加到切片末尾，并返回一个新的切片：

```go
slice := []int{1, 2, 3}
slice = append(slice, 4)        // [1, 2, 3, 4]
slice = append(slice, 5, 6, 7)  // [1, 2, 3, 4, 5, 6, 7]

// 将一个切片追加到另一个切片
other := []int{8, 9, 10}
slice = append(slice, other...)  // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

#### 对切片进行切片

可以使用切片操作符从切片中创建新的切片：

```go
slice := []int{1, 2, 3, 4, 5}
sub := slice[1:3]  // [2, 3]
```

#### 复制切片

`copy` 函数将元素从一个切片复制到另一个切片：

```go
src := []int{1, 2, 3}
dst := make([]int, len(src))
n := copy(dst, src)  // n 是复制的元素数量（3）
```

### 常见的切片算法

#### 查找最大值

查找整数切片中的最大值：

```go
func findMax(numbers []int) int {
    if len(numbers) == 0 {
        return 0  // 或其他默认值
    }
    
    max := numbers[0]
    for _, n := range numbers[1:] {
        if n > max {
            max = n
        }
    }
    return max
}
```

#### 去除重复项

在保持顺序的前提下去除重复项：

```go
func removeDuplicates(numbers []int) []int {
    if len(numbers) == 0 {
        return []int{}
    }
    
    // 使用 map 记录已见过的值
    seen := make(map[int]bool)
    result := make([]int, 0, len(numbers))
    
    for _, n := range numbers {
        if !seen[n] {
            seen[n] = true
            result = append(result, n)
        }
    }
    
    return result
}
```

#### 反转切片

反转切片中元素的顺序：

```go
func reverseSlice(slice []int) []int {
    result := make([]int, len(slice))
    for i, v := range slice {
        result[len(slice)-1-i] = v
    }
    return result
}

// 另一种方法，直接修改原切片
func reverseInPlace(slice []int) {
    for i, j := 0, len(slice)-1; i < j; i, j = i+1, j-1 {
        slice[i], slice[j] = slice[j], slice[i]
    }
}
```

#### 过滤元素

根据条件过滤元素（例如，仅保留偶数）：

```go
func filterEven(numbers []int) []int {
    result := make([]int, 0)
    for _, n := range numbers {
        if n%2 == 0 {
            result = append(result, n)
        }
    }
    return result
}
```

### 切片陷阱与技巧

#### 切片的修改行为

切片是数组的引用，因此修改切片会同时修改底层数组：

```go
original := []int{1, 2, 3, 4, 5}
sub := original[1:3]
sub[0] = 42  // 同样会修改 original

fmt.Println(original)  // [1, 42, 3, 4, 5]
```

#### 创建独立副本

要创建切片的独立副本：

```go
original := []int{1, 2, 3, 4, 5}
copy := make([]int, len(original))
copy = append(copy, original...)
```

#### 预分配切片

在逐步构建切片时，预分配容量以提高效率：

```go
// 效率较低
var result []int
for i := 0; i < 10000; i++ {
    result = append(result, i)  // 多次分配和拷贝
}

// 效率较高
result := make([]int, 0, 10000)
for i := 0; i < 10000; i++ {
    result = append(result, i)  // 无需重新分配
}
```

#### 空切片与 nil 切片

空切片长度为 0，但不是 nil：

```go
var nilSlice []int         // nil，长度 0，容量 0
emptySlice := []int{}      // 不是 nil，长度 0，容量 0
emptyMake := make([]int, 0) // 不是 nil，长度 0，容量 0

fmt.Println(nilSlice == nil)   // true
fmt.Println(emptySlice == nil) // false
```

## 进一步阅读

- [Go 切片：用法与内部原理](https://go.dev/blog/slices-intro)
- [Go by Example：切片](https://gobyexample.com/slices)
- [《Go 编程语言规范》：切片类型](https://go.dev/ref/spec#Slice_types)