# 温度转换器提示

## 提示 1：温度转换公式
关键转换公式：
- 摄氏度转华氏度：`F = C × 9/5 + 32`
- 华氏度转摄氏度：`C = (F - 32) × 5/9`
- 摄氏度转开尔文：`K = C + 273.15`
- 开尔文转摄氏度：`C = K - 273.15`

## 提示 2：函数结构
创建独立的转换函数：
```go
func CelsiusToFahrenheit(celsius float64) float64 {
    return celsius*9/5 + 32
}

func FahrenheitToCelsius(fahrenheit float64) float64 {
    return (fahrenheit - 32) * 5 / 9
}
```

## 提示 3：开尔文转换
记住开尔文的绝对零度：
```go
func CelsiusToKelvin(celsius float64) float64 {
    return celsius + 273.15
}

func KelvinToCelsius(kelvin float64) float64 {
    return kelvin - 273.15
}
```

## 提示 4：链式转换
对于华氏度 ↔ 开尔文，通过摄氏度中转：
```go
func FahrenheitToKelvin(fahrenheit float64) float64 {
    celsius := FahrenheitToCelsius(fahrenheit)
    return CelsiusToKelvin(celsius)
}
```

## 提示 5：输入验证
验证温度是否符合物理极限：
```go
func isValidKelvin(kelvin float64) bool {
    return kelvin >= 0 // 绝对零度
}

func isValidCelsius(celsius float64) bool {
    return celsius >= -273.15 // 摄氏度下的绝对零度
}
```