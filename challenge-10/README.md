[查看排行榜](SCOREBOARD.md)

# 挑战 10：多态形状计算器

## 问题描述

使用 Go 接口实现一个系统，用于计算各种几何形状的属性。本挑战重点在于理解和正确实现 Go 的接口系统，以实现多态性。

## 要求

1. 实现一个 `Shape` 接口，包含以下方法：
   - `Area() float64`：计算形状的面积
   - `Perimeter() float64`：计算形状的周长（或圆周长）
   - `String() string`：返回形状的字符串表示（实现 fmt.Stringer）

2. 实现以下具体形状：
   - `Rectangle`：由宽度和高度定义
   - `Circle`：由半径定义
   - `Triangle`：由三条边定义（使用海伦公式计算面积）

3. 实现一个 `ShapeCalculator`，能够：
   - 接受任意形状并返回其属性
   - 计算多个形状的总面积
   - 从一组形状中找出面积最大的形状
   - 按面积升序或降序对形状进行排序

## 函数签名

```go
// Shape 接口
type Shape interface {
    Area() float64
    Perimeter() float64
    fmt.Stringer // 包含 String() string 方法
}

// 具体类型
type Rectangle struct {
    Width, Height float64
}

type Circle struct {
    Radius float64
}

type Triangle struct {
    SideA, SideB, SideC float64
}

// 构造函数
func NewRectangle(width, height float64) (*Rectangle, error)
func NewCircle(radius float64) (*Circle, error)
func NewTriangle(a, b, c float64) (*Triangle, error)

// ShapeCalculator
type ShapeCalculator struct{}

func NewShapeCalculator() *ShapeCalculator
func (sc *ShapeCalculator) PrintProperties(s Shape)
func (sc *ShapeCalculator) TotalArea(shapes []Shape) float64
func (sc *ShapeCalculator) LargestShape(shapes []Shape) Shape
func (sc *ShapeCalculator) SortByArea(shapes []Shape, ascending bool) []Shape
```

## 约束条件

- 所有测量值必须为正值
- 三角形的三边必须满足三角不等式定理（任意两边之和必须大于第三边的长度）
- 在构造函数中实现适当的验证，并返回相应的错误
- 计算圆形属性时使用 π（pi）的常量
- `String()` 方法应返回格式化的字符串，包含形状类型和尺寸

## 示例用法

```go
// 创建形状
rect, _ := NewRectangle(5, 3)
circle, _ := NewCircle(4)
triangle, _ := NewTriangle(3, 4, 5)

// 多态地使用形状
calculator := NewShapeCalculator()
shapes := []Shape{rect, circle, triangle}

// 计算总面积
totalArea := calculator.TotalArea(shapes)
fmt.Printf("总面积: %.2f\n", totalArea)

// 按面积排序形状
sortedShapes := calculator.SortByArea(shapes, true)
for _, s := range sortedShapes {
    calculator.PrintProperties(s)
}

// 找出面积最大的形状
largest := calculator.LargestShape(shapes)
fmt.Printf("面积最大的形状: %s，面积为 %.2f\n", largest, largest.Area())
```

## 指导说明

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-10/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的接口、类型和方法。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-10/` 目录下运行以下命令：

```bash
go test -v
```