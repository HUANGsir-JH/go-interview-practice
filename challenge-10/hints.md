# 多态形状计算器的提示

## 提示 1：接口定义
定义具有所需方法的Shape接口：
```go
type Shape interface {
    Area() float64
    Perimeter() float64
    fmt.Stringer // 嵌入String() string
}
```

## 提示 2：矩形实现
实现Rectangle结构体及其方法：
```go
type Rectangle struct {
    Width, Height float64
}

func (r *Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r *Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}
```

## 提示 3：圆形实现
对于圆形计算，使用`math.Pi`：
```go
func (c *Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c *Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}
```

## 提示 4：使用海伦公式计算三角形面积
使用海伦公式实现三角形面积：
```go
func (t *Triangle) Area() float64 {
    s := (t.SideA + t.SideB + t.SideC) / 2 // 半周长
    return math.Sqrt(s * (s - t.SideA) * (s - t.SideB) * (s - t.SideC))
}
```

## 提示 5：构造函数验证
在构造函数中验证输入：
```go
func NewTriangle(a, b, c float64) (*Triangle, error) {
    if a <= 0 || b <= 0 || c <= 0 {
        return nil, errors.New("边长必须为正数")
    }
    
    // 三角形不等式：任意两边之和大于第三边
    if a+b <= c || a+c <= b || b+c <= a {
        return nil, errors.New("边长不能构成有效三角形")
    }
    
    return &Triangle{SideA: a, SideB: b, SideC: c}, nil
}
```

## 提示 6：String方法实现
为每个形状实现String方法：
```go
func (r *Rectangle) String() string {
    return fmt.Sprintf("Rectangle(width=%.2f, height=%.2f)", r.Width, r.Height)
}

func (c *Circle) String() string {
    return fmt.Sprintf("Circle(radius=%.2f)", c.Radius)
}
```

## 提示 7：总面积计算
遍历形状并累加它们的面积：
```go
func (sc *ShapeCalculator) TotalArea(shapes []Shape) float64 {
    var total float64
    for _, shape := range shapes {
        total += shape.Area()
    }
    return total
}
```

## 提示 8：查找最大形状
比较面积以找到最大的：
```go
func (sc *ShapeCalculator) LargestShape(shapes []Shape) Shape {
    if len(shapes) == 0 {
        return nil
    }
    
    largest := shapes[0]
    for _, shape := range shapes[1:] {
        if shape.Area() > largest.Area() {
            largest = shape
        }
    }
    return largest
}
```

## 提示 9：按面积排序
使用`sort.Slice`按面积排序形状：
```go
func (sc *ShapeCalculator) SortByArea(shapes []Shape, ascending bool) []Shape {
    sorted := make([]Shape, len(shapes))
    copy(sorted, shapes)
    
    sort.Slice(sorted, func(i, j int) bool {
        if ascending {
            return sorted[i].Area() < sorted[j].Area()
        }
        return sorted[i].Area() > sorted[j].Area()
    })
    
    return sorted
}
```

## 提示 10：PrintProperties方法
使用接口打印形状信息：
```go
func (sc *ShapeCalculator) PrintProperties(s Shape) {
    fmt.Printf("Shape: %s\n", s)
    fmt.Printf("Area: %.2f\n", s.Area())
    fmt.Printf("Perimeter: %.2f\n", s.Perimeter())
}
```