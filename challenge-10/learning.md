# 多态形状计算器学习材料

## Go中的接口与多态性

本挑战聚焦于使用Go的接口来实现几何形状计算的多态性。

### 理解Go中的接口

在Go中，接口定义行为而不指定实现。接口是一组方法签名的集合：

```go
// 定义一个接口
type Shape interface {
    Area() float64
    Perimeter() float64
}
```

一个类型通过实现其方法隐式地实现接口：

```go
// Rectangle 实现了 Shape 接口
type Rectangle struct {
    Width  float64
    Height float64
}

// 实现 Area 方法
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 实现 Perimeter 方法
func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

// Circle 也实现了 Shape 接口
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}
```

### 使用接口实现多态性

接口允许多态行为——不同类型的对象可以基于其行为被统一处理：

```go
// 可以处理任意 Shape 的函数
func PrintShapeInfo(s Shape) {
    fmt.Printf("面积: %.2f\n", s.Area())
    fmt.Printf("周长: %.2f\n", s.Perimeter())
}

// 使用示例
rect := Rectangle{Width: 5, Height: 3}
circ := Circle{Radius: 2}

PrintShapeInfo(rect)  // 适用于 Rectangle
PrintShapeInfo(circ)  // 适用于 Circle
```

### 接口值

接口值由两个部分组成：
1. 动态类型：存储在接口中的具体类型
2. 动态值：该类型的实际值

```go
var s Shape                // nil 接口值（nil 类型，nil 值）
s = Rectangle{5, 3}        // s 的类型为 Rectangle，值为 Rectangle{5, 3}
s = Circle{2.5}            // s 现在的类型为 Circle，值为 Circle{2.5}
```

### 空接口

空接口 `interface{}` 或 `any`（Go 1.18+）没有方法，可以容纳任何值：

```go
func PrintAny(a interface{}) {
    fmt.Println(a)
}

PrintAny(42)              // 适用于 int
PrintAny("Hello")         // 适用于 string
PrintAny(Rectangle{5, 3}) // 适用于 Rectangle
```

### 类型断言

类型断言用于从接口中提取底层值：

```go
// 单返回值类型断言
rect := s.(Rectangle) // 如果 s 不是 Rectangle，则会恐慌

// 带检查的类型断言
rect, ok := s.(Rectangle)
if ok {
    fmt.Println("这是一个矩形，宽度为:", rect.Width)
} else {
    fmt.Println("这不是一个矩形")
}
```

### 类型开关

类型开关可处理多种类型：

```go
func Describe(s Shape) string {
    switch v := s.(type) {
    case Rectangle:
        return fmt.Sprintf("矩形，宽度 %.2f，高度 %.2f", v.Width, v.Height)
    case Circle:
        return fmt.Sprintf("圆形，半径 %.2f", v.Radius)
    case nil:
        return "空形状"
    default:
        return fmt.Sprintf("未知形状，类型 %T", v)
    }
}
```

### 接口组合

接口可以由其他接口组合而成：

```go
type Sizer interface {
    Area() float64
}

type Perimeterer interface {
    Perimeter() float64
}

// 组合接口
type Shape interface {
    Sizer
    Perimeterer
    String() string  // 额外的方法
}
```

### 接口嵌入

Go 允许将一个接口嵌入到另一个接口中：

```go
type Stringer interface {
    String() string
}

type Shape interface {
    Area() float64
    Perimeter() float64
}

// CompleteShape 嵌入 Shape 和 Stringer
type CompleteShape interface {
    Shape
    Stringer
}
```

### 使用指针接收器实现接口

方法接收器类型对于接口实现很重要：

```go
type Modifier interface {
    Scale(factor float64)
}

// 值接收器 - 不修改原始值
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 指针接收器 - 修改原始值
func (r *Rectangle) Scale(factor float64) {
    r.Width *= factor
    r.Height *= factor
}

var m Modifier
r := Rectangle{5, 3}

// 这样可以工作 - r 是可寻址的
m = &r
m.Scale(2)

// 这样不行 - 接口期望指针接收器
// m = r // 编译错误
```

### 接口最佳实践

1. **保持接口简洁**：优先选择方法较少的接口（通常只有一个方法）
2. **在使用点定义接口**：在使用接口的包中定义，而不是在实现处定义
3. **接口代表行为而非类型**：关注对象能做什么，而不是它是什么

```go
// 良好 - 定义行为
type Reader interface {
    Read(p []byte) (n int, err error)
}

// 不太好 - 定义类型
type Car interface {
    Drive()
    Stop()
    Refuel()
}
```

### 里氏替换原则

里氏替换原则指出，父类的对象应能被子类的对象替换，而不会影响程序的正确性：

```go
// 常见的违反情况是在子类型中增加要求
type Parallelogram interface {
    SetWidth(w float64)
    SetHeight(h float64)
    Area() float64
}

type Rectangle struct {
    width, height float64
}

func (r *Rectangle) SetWidth(w float64) { r.width = w }
func (r *Rectangle) SetHeight(h float64) { r.height = h }
func (r Rectangle) Area() float64 { return r.width * r.height }

type Square struct {
    side float64
}

// 此实现破坏了预期！
func (s *Square) SetWidth(w float64) {
    s.side = w
    // 设置一个维度时，正方形会同时改变两个维度
}

func (s *Square) SetHeight(h float64) {
    s.side = h
}

func (s Square) Area() float64 { return s.side * s.side }
```

### 实际示例：形状计算器

让我们实现一个完整的形状计算器：

```go
package shape

import (
    "fmt"
    "math"
)

// Shape 是基本接口
type Shape interface {
    Area() float64
    Perimeter() float64
    String() string
}

// Circle 实现
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

func (c Circle) String() string {
    return fmt.Sprintf("圆(半径=%.2f)", c.Radius)
}

// Rectangle 实现
type Rectangle struct {
    Width  float64
    Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

func (r Rectangle) String() string {
    return fmt.Sprintf("矩形(宽度=%.2f, 高度=%.2f)", r.Width, r.Height)
}

// Triangle 实现
type Triangle struct {
    SideA float64
    SideB float64
    SideC float64
}

func (t Triangle) Perimeter() float64 {
    return t.SideA + t.SideB + t.SideC
}

func (t Triangle) Area() float64 {
    // 海伦公式
    s := t.Perimeter() / 2
    return math.Sqrt(s * (s - t.SideA) * (s - t.SideB) * (s - t.SideC))
}

func (t Triangle) String() string {
    return fmt.Sprintf("三角形(边长=%.2f, %.2f, %.2f)", t.SideA, t.SideB, t.SideC)
}

// ShapeCalculator 处理多个形状
type ShapeCalculator struct {
    shapes []Shape
}

func NewCalculator() *ShapeCalculator {
    return &ShapeCalculator{shapes: make([]Shape, 0)}
}

func (c *ShapeCalculator) AddShape(s Shape) {
    c.shapes = append(c.shapes, s)
}

func (c *ShapeCalculator) TotalArea() float64 {
    total := 0.0
    for _, s := range c.shapes {
        total += s.Area()
    }
    return total
}

func (c *ShapeCalculator) TotalPerimeter() float64 {
    total := 0.0
    for _, s := range c.shapes {
        total += s.Perimeter()
    }
    return total
}

func (c *ShapeCalculator) ListShapes() []string {
    result := make([]string, len(c.shapes))
    for i, s := range c.shapes {
        result[i] = s.String()
    }
    return result
}
```

### 扩展新形状

接口的一个优势是可以添加新类型而无需更改现有代码：

```go
// 添加新形状：正多边形
type RegularPolygon struct {
    Sides     int
    SideLength float64
}

func (p RegularPolygon) Perimeter() float64 {
    return float64(p.Sides) * p.SideLength
}

func (p RegularPolygon) Area() float64 {
    return (float64(p.Sides) * p.SideLength * p.SideLength) / (4 * math.Tan(math.Pi/float64(p.Sides)))
}

func (p RegularPolygon) String() string {
    return fmt.Sprintf("正多边形(边数=%d, 边长=%.2f)", p.Sides, p.SideLength)
}

// 无需修改即可与现有计算器兼容
calculator.AddShape(RegularPolygon{Sides: 6, SideLength: 5})
```

### 使用接口进行测试

接口通过允许模拟实现来促进测试：

```go
// 接口定义
type AreaCalculator interface {
    Area() float64
}

// 使用接口的函数
func IsLargeShape(s AreaCalculator) bool {
    return s.Area() > 100
}

// 使用模拟进行测试
type MockShape struct{
    MockArea float64
}

func (m MockShape) Area() float64 {
    return m.MockArea
}

func TestIsLargeShape(t *testing.T) {
    small := MockShape{50}
    large := MockShape{150}
    
    if IsLargeShape(small) {
        t.Error("期望小形状不是大形状")
    }
    
    if !IsLargeShape(large) {
        t.Error("期望大形状是大形状")
    }
}
```

## 进一步阅读

- [Go 接口教程](https://tour.golang.org/methods/9)
- [Effective Go：接口](https://golang.org/doc/effective_go#interfaces)
- [Go 中的 SOLID 设计](https://dave.cheney.net/2016/08/20/solid-go-design)
- [反射法则](https://blog.golang.org/laws-of-reflection)（用于更深入理解接口）