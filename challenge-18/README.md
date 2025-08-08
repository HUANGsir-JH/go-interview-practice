[查看排行榜](SCOREBOARD.md)

# 挑战 18：温度转换器

## 问题描述

编写一个程序，实现摄氏度与华氏度之间的温度转换。你需要实现两个函数：
1. `CelsiusToFahrenheit` - 将摄氏度转换为华氏度。
2. `FahrenheitToCelsius` - 将华氏度转换为摄氏度。

## 函数签名

```go
func CelsiusToFahrenheit(celsius float64) float64
func FahrenheitToCelsius(fahrenheit float64) float64
```

## 输入格式

- 一个 float64 类型的温度值，单位为摄氏度或华氏度。

## 输出格式

- 一个 float64 类型的温度值，已转换为另一种单位。

## 转换公式

- **摄氏度转华氏度**：F = C × 9/5 + 32
- **华氏度转摄氏度**：C = (F - 32) × 5/9

## 示例输入与输出

### 示例输入 1

```
CelsiusToFahrenheit(0)
```

### 示例输出 1

```
32.0
```

### 示例输入 2

```
FahrenheitToCelsius(32)
```

### 示例输出 2

```
0.0
```

### 示例输入 3

```
CelsiusToFahrenheit(100)
```

### 示例输出 3

```
212.0
```

## 要求

1. 将结果四舍五入到小数点后两位
2. 正确处理负温度
3. 函数应能处理任何有效的温度值

## 指导步骤

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-18/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现**所需的函数。
- 通过运行测试文件在本地测试你的解决方案。
- **Commit** 并 **push** 代码到你的副本。
- **创建**一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-18/` 目录下运行以下命令：

```bash
go test -v
```