# 学习：Fiber Web 框架基础

## 🌟 **什么是 Fiber？**

Fiber 是一个受 Express.js 启发的 Web 框架，基于 Fasthttp 构建，Fasthttp 是 Go 语言中最快的 HTTP 引擎。Fiber 旨在为快速开发提供便利，同时兼顾零内存分配和高性能。

### **为什么选择 Fiber？**
- **快速**：基于 Fasthttp，是最快的 HTTP 引擎之一
- **低内存**：零内存分配的路由器
- **类 Express**：如果你熟悉 Express.js，那么你已经掌握了 Fiber
- **丰富的中间件**：提供 40 多个中间件包
- **开发者友好**：简单的路由、静态文件支持和模板引擎

## 🏗️ **核心概念**

### **1. App 实例**
App 实例是 Fiber 应用的核心。它负责处理传入的 HTTP 请求，并将请求路由到相应的处理器。

```go
app := fiber.New() // 创建新的 Fiber 实例
// 或者带配置
app := fiber.New(fiber.Config{
    Prefork: true,
    CaseSensitive: true,
})
```

### **2. HTTP 方法**
Fiber 支持所有标准 HTTP 方法，语法与 Express 类似：
- **GET**：获取数据
- **POST**：创建新资源
- **PUT**：更新整个资源
- **PATCH**：部分更新
- **DELETE**：删除资源
- **HEAD**：仅获取头部信息
- **OPTIONS**：检查允许的方法

### **3. 上下文（fiber.Ctx）**
上下文携带请求数据，验证 JSON，并渲染响应。

```go
func handler(c *fiber.Ctx) error {
    // c 包含关于 HTTP 请求/响应的所有信息
    return c.JSON(fiber.Map{"message": "Hello"})
}
```

## 📡 **HTTP 请求/响应流程**

### **理解流程**
1. **客户端** 发送 HTTP 请求
2. **路由器** 将 URL 模式匹配到对应的处理器
3. **处理器** 处理请求并准备响应
4. **服务器** 将响应返回给客户端

### **请求组成部分**
- **方法**：GET、POST、PUT、DELETE
- **URL**：`/tasks/123`
- **头信息**：Content-Type、Authorization
- **正文**：JSON、表单数据等

### **响应组成部分**
- **状态码**：200、404、500 等
- **头信息**：Content-Type、Cache-Control
- **正文**：JSON、HTML、纯文本

## 🛣️ **路由模式**

### **静态路由**
```go
app.Get("/", func(c *fiber.Ctx) error {
    return c.SendString("Hello, World!")
})
```

### **路由参数**
```go
app.Get("/tasks/:id", func(c *fiber.Ctx) error {
    id := c.Params("id")
    return c.JSON(fiber.Map{"task_id": id})
})
```

### **查询参数**
```go
app.Get("/tasks", func(c *fiber.Ctx) error {
    search := c.Query("search", "")
    return c.JSON(fiber.Map{"search": search})
})
```

## 📝 **请求/响应处理**

### **JSON 响应**
```go
app.Get("/api/data", func(c *fiber.Ctx) error {
    data := map[string]interface{}{
        "message": "Success",
        "data": []string{"item1", "item2"},
    }
    return c.JSON(data)
})
```

### **JSON 解析**
```go
type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

app.Post("/users", func(c *fiber.Ctx) error {
    user := new(User)
    if err := c.BodyParser(user); err != nil {
        return c.Status(400).JSON(fiber.Map{"error": err.Error()})
    }
    return c.JSON(user)
})
```

## 🔧 **常用方法**

### **上下文方法**
- `c.Params(key)` - 获取路由参数
- `c.Query(key)` - 获取查询参数
- `c.BodyParser(&struct)` - 解析请求体
- `c.JSON(data)` - 发送 JSON 响应
- `c.Status(code)` - 设置状态码
- `c.SendString(text)` - 发送纯文本

### **响应辅助方法**
```go
// 状态码
c.Status(fiber.StatusOK)        // 200
c.Status(fiber.StatusNotFound)  // 404
c.Status(fiber.StatusCreated)   // 201

// JSON 响应
c.JSON(fiber.Map{"key": "value"})
c.Status(400).JSON(fiber.Map{"error": "Bad request"})
```

## 🚀 **性能优势**

### **内存效率**
- 零内存分配的路由器
- 快速的 HTTP 解析
- 低内存占用

### **框架特性**
- **基于 Fasthttp**：Go 语言高性能 HTTP 引擎
- **类 Express API**：JavaScript 开发者熟悉的使用体验
- **丰富的生态系统**：大量中间件和社区支持

## 📚 **最佳实践**

1. **错误处理**：始终从处理器返回错误
2. **状态码**：使用适当的 HTTP 状态码
3. **JSON 验证**：解析并验证请求体
4. **上下文使用**：使用上下文进行请求/响应操作
5. **路由组织**：将相关路由分组

## 🔗 **框架特性**

### **Fiber 的关键特性**
- **API 风格**：受 Express.js 启发的语法和模式
- **学习曲线**：对熟悉 Express.js 的开发者来说很容易上手
- **内存使用**：优化为低内存占用
- **中间件**：拥有丰富的内置和第三方中间件生态

## 🎯 **下一步**

掌握基本路由后，你将学习：
1. **中间件** - 请求/响应处理
2. **验证** - 输入验证与错误处理
3. **认证** - JWT 令牌与安全机制
4. **高级功能** - 生产环境就绪的模式