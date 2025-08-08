# 实现提示

## 快速入门

1. **创建 Fiber 应用**
   ```go
   app := fiber.New()
   ```

2. **基本路由结构**
   ```go
   app.Get("/path", func(c *fiber.Ctx) error {
       // 你的处理逻辑
       return c.JSON(response)
   })
   ```

## 分步实现

### 1. 健康检查端点 (`GET /ping`)
```go
app.Get("/ping", func(c *fiber.Ctx) error {
    return c.JSON(fiber.Map{
        "message": "pong",
    })
})
```

### 2. 获取所有任务 (`GET /tasks`)
```go
app.Get("/tasks", func(c *fiber.Ctx) error {
    tasks := taskStore.GetAll()
    return c.JSON(tasks)
})
```

### 3. 根据 ID 获取任务 (`GET /tasks/:id`)
```go
app.Get("/tasks/:id", func(c *fiber.Ctx) error {
    // 从 URL 参数中提取 ID
    idStr := c.Params("id")
    
    // 将字符串转换为整数
    id, err := strconv.Atoi(idStr)
    if err != nil {
        return c.Status(400).JSON(fiber.Map{
            "error": "无效的任务 ID",
        })
    }
    
    // 从存储中获取任务
    task, exists := taskStore.GetByID(id)
    if !exists {
        return c.Status(404).JSON(fiber.Map{
            "error": "未找到任务",
        })
    }
    
    return c.JSON(task)
})
```

### 4. 创建任务 (`POST /tasks`)
```go
app.Post("/tasks", func(c *fiber.Ctx) error {
    var newTask Task
    
    // 解析 JSON 请求体到结构体
    if err := c.BodyParser(&newTask); err != nil {
        return c.Status(400).JSON(fiber.Map{
            "error": "无效的 JSON",
        })
    }
    
    // 在存储中创建任务
    task := taskStore.Create(newTask.Title, newTask.Description, newTask.Completed)
    
    // 返回 201 Created 状态
    return c.Status(201).JSON(task)
})
```

### 5. 更新任务 (`PUT /tasks/:id`)
```go
app.Put("/tasks/:id", func(c *fiber.Ctx) error {
    // 提取并验证 ID
    idStr := c.Params("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        return c.Status(400).JSON(fiber.Map{
            "error": "无效的任务 ID",
        })
    }
    
    // 解析更新数据
    var updateTask Task
    if err := c.BodyParser(&updateTask); err != nil {
        return c.Status(400).JSON(fiber.Map{
            "error": "无效的 JSON",
        })
    }
    
    // 在存储中更新
    task, exists := taskStore.Update(id, updateTask.Title, updateTask.Description, updateTask.Completed)
    if !exists {
        return c.Status(404).JSON(fiber.Map{
            "error": "未找到任务",
        })
    }
    
    return c.JSON(task)
})
```

### 6. 删除任务 (`DELETE /tasks/:id`)
```go
app.Delete("/tasks/:id", func(c *fiber.Ctx) error {
    // 提取并验证 ID
    idStr := c.Params("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        return c.Status(400).JSON(fiber.Map{
            "error": "无效的任务 ID",
        })
    }
    
    // 从存储中删除
    if !taskStore.Delete(id) {
        return c.Status(404).JSON(fiber.Map{
            "error": "未找到任务",
        })
    }
    
    // 返回 204 无内容
    return c.SendStatus(204)
})
```

### 7. 启动服务器
```go
// 在端口 3000 上启动服务器
app.Listen(":3000")
```

## 关键 Fiber 方法

- **`c.Params(key)`** - 提取 URL 参数
- **`c.BodyParser(&struct)`** - 解析 JSON 请求体
- **`c.JSON(data)`** - 发送 JSON 响应
- **`c.Status(code)`** - 设置 HTTP 状态码
- **`c.SendStatus(code)`** - 仅发送状态码
- **`fiber.Map{}`** - 快速创建 JSON 对象

## 常见模式

### 错误响应
```go
return c.Status(400).JSON(fiber.Map{
    "error": "错误信息",
})
```

### 带数据的成功响应
```go
return c.JSON(data)
```

### 已创建响应
```go
return c.Status(201).JSON(createdData)
```

### 无内容响应
```go
return c.SendStatus(204)
```

## 测试提示

1. 使用提供的测试文件来验证你的实现
2. 使用以下命令运行测试：`go test -v`
3. 检查所有 HTTP 状态码是否正确
4. 确保 JSON 响应格式符合预期

## 故障排除

- **导入错误**：确保 `go.mod` 正确配置了 Fiber 依赖
- **JSON 解析**：确保请求的 Content-Type 为 `application/json`
- **状态码**：记得设置适当的代码（200、201、404 等）
- **并发**：提供的 TaskStore 已为你处理线程安全问题