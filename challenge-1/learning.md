# 两数之和学习资料

## Go 基础语法与函数

在 Go 中，函数是一等公民，使用 `func` 关键字定义。本挑战聚焦于基础函数实现以及理解 Go 的算术运算符语法。

### 函数声明

```go
// 基础函数结构
func FunctionName(parameter1 Type1, parameter2 Type2) return type {
    // 函数体
    return return value
}
```

例如，一个将两个整数相加的函数应为：

```go
func Add(a int, b int) int {
    return a + b
}
```

你也可以一次性为多个相同类型的参数指定类型：

```go
func Add(a, b int) int {
    return a + b
}
```

### Go 中的基本数据类型

Go 拥有多种基本类型，包括：

- **数值类型**：
  - `int`, `int8`, `int16`, `int32`, `int64`
  - `uint`, `uint8`, `uint16`, `uint32`, `uint64`, `uintptr`
  - `float32`, `float64`
  - `complex64`, `complex128`
- **字符串类型**：`string`
- **布尔类型**：`bool`

本挑战中我们使用 `int` 类型。

### 算术运算符

Go 支持以下算术运算符：

- 加法：`+`
- 减法：`-`
- 乘法：`*`
- 除法：`/`
- 取模：`%`（除法后的余数）

### Go 中的变量

Go 变量使用 `var` 关键字或短声明操作符（`:=`）声明：

```go
// 使用 var
var a int = 10
var b int = 20

// 短声明（类型自动推断）
a := 10
b := 20
```

### Go 中的测试

Go 在 `testing` 包中内置了测试框架。测试是函数，以 `Test` 开头，并且名称以大写字母开头。

```go
func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}
```

### Go 的设计哲学

Go 的设计原则是简洁、可读性和高效性。它鼓励：

- 清晰简洁的代码
- 强类型
- 高效的编译和执行
- 内置并发支持（尽管本挑战不需要）

## 进一步阅读

- [Go 之旅](https://tour.golang.org/welcome/1) - Go 的交互式入门教程
- [有效 Go](https://golang.org/doc/effective_go) - 编写清晰、符合习惯的 Go 代码的建议
- [Go 示例：函数](https://gobyexample.com/functions) - Go 函数的实际示例