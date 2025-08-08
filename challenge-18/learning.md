# 温度转换器学习材料

## 在 Go 中处理浮点数

### 基本浮点类型

Go 有两种浮点数类型：
- `float32` - 32位浮点数（单精度）
- `float64` - 64位浮点数（双精度）

对于大多数应用，推荐使用 `float64`，因为它提供了更高的精度。

```go
var temperature float64 = 23.5
```

### 算术运算

浮点数支持标准的算术运算：

```go
var celsius float64 = 25.0
var fahrenheit float64

// 加法
fahrenheit = celsius + 20.0 // 45.0

// 减法
celsius = celsius - 5.0 // 20.0

// 乘法
fahrenheit = celsius * 1.8 // 36.0

// 除法
celsius = fahrenheit / 1.8 // 20.0
```

### 精度与舍入

由于数字在二进制中表示的限制，浮点数运算存在精度限制，这可能导致微小的不准确。

例如，表达式 `0.1 + 0.2` 可能不会精确等于 `0.3`，而是非常接近的值，如 `0.30000000000000004`。

为处理这种情况，可以将数字四舍五入到指定的小数位数：

```go
import "math"

func Round(value float64, decimals int) float64 {
    precision := math.Pow10(decimals)
    return math.Round(value*precision) / precision
}

// 使用示例
x := 0.1 + 0.2                  // 0.30000000000000004
rounded := Round(x, 1)          // 0.3
```

### 温度转换

摄氏度与华氏度之间转换的标准公式如下：

1. **摄氏度转华氏度**：F = C × 9/5 + 32  
2. **华氏度转摄氏度**：C = (F - 32) × 5/9

以下是用 Go 实现这些转换的方法：

```go
func CelsiusToFahrenheit(celsius float64) float64 {
    return celsius*9.0/5.0 + 32.0
}

func FahrenheitToCelsius(fahrenheit float64) float64 {
    return (fahrenheit - 32.0) * 5.0 / 9.0
}
```

### 格式化浮点输出

在显示浮点数时，通常希望以特定的小数位数进行格式化。可以使用 `fmt` 包来实现：

```go
import "fmt"

celsius := 25.0
fahrenheit := CelsiusToFahrenheit(celsius)

// 保留两位小数输出
fmt.Printf("%.2f°C 等于 %.2f°F\n", celsius, fahrenheit)
// 输出：25.00°C 等于 77.00°F
```

### 常量与数学运算

对于数学运算，Go 提供了 `math` 包，包含常量和函数：

```go
import "math"

// 常量
pi := math.Pi                // 3.141592653589793
e := math.E                   // 2.718281828459045

// 函数
absValue := math.Abs(-15.5)  // 15.5
sqrt := math.Sqrt(16)        // 4.0
power := math.Pow(2, 3)      // 8.0 (2³)
```

### 无效输入的错误处理

在进行温度转换时，可能需要验证输入或处理边界情况：

```go
// 检查摄氏度是否低于绝对零度
func ValidateCelsius(celsius float64) error {
    if celsius < -273.15 {
        return fmt.Errorf("温度低于绝对零度: %f°C", celsius)
    }
    return nil
}

// 检查华氏度是否低于绝对零度
func ValidateFahrenheit(fahrenheit float64) error {
    if fahrenheit < -459.67 {
        return fmt.Errorf("温度低于绝对零度: %f°F", fahrenheit)
    }
    return nil
}
```

### 其他温标

虽然本练习聚焦于摄氏度和华氏度，但还有其他温标：

1. **开尔文 (K)**：K = C + 273.15  
2. **兰金 (°R)**：°R = F + 459.67  
3. **列氏 (°Ré)**：°Ré = C × 0.8  

要构建一个完整的温度转换库，可以实现所有这些温标之间的转换。

## 进一步阅读

- [Go by Example: 浮点数](https://gobyexample.com/floating-point)
- [IEEE 754 标准](https://en.wikipedia.org/wiki/IEEE_754) - 浮点数运算的标准
- [温度单位换算公式](https://en.wikipedia.org/wiki/Conversion_of_scales_of_temperature)
- [math 包文档](https://pkg.go.dev/math)