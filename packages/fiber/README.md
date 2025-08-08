# Fiber Web 开发挑战

使用 Fiber 框架掌握高性能 Go 语言 Web 开发。本套包包含 4 个循序渐进的挑战，带你从基础 HTTP 概念逐步过渡到使用 Fiber 的 Express 风格 API 构建高级生产就绪模式。

## 挑战概览

### 🎯 [挑战 1：基础路由](./challenge-1-basic-routing/)
**难度：** 初学者 | **时长：** 30-45 分钟

通过构建一个简单的任务管理 API 来学习 Fiber 的基础知识，涵盖基础路由、请求处理和 JSON 响应。

**核心技能：**
- 基础 Fiber 应用设置
- 路由处理器与 HTTP 方法
- JSON 请求/响应处理
- 路径参数
- 查询参数

**涵盖主题：**
- `fiber.App` 基础知识
- 路由定义与处理器
- 上下文处理
- JSON 序列化/反序列化
- 错误响应

---

### 🚀 [挑战 2：中间件与请求/响应处理](./challenge-2-middleware/)
**难度：** 中级 | **时长：** 45-60 分钟

构建一个增强版博客 API，涵盖全面的中间件模式，包括日志记录、认证、CORS 和限流。

**核心技能：**
- 自定义中间件创建
- 请求 ID 生成与追踪
- 限流实现
- CORS 处理
- 认证中间件

**涵盖主题：**
- 请求/响应日志记录
- API 密钥认证
- 跨域请求处理
- 按 IP 限流
- 集中式错误处理

---

### 📦 [挑战 3：验证与错误处理](./challenge-3-validation-errors/)
**难度：** 中级 | **时长：** 60-75 分钟

构建一个产品目录 API，包含全面的输入验证、自定义验证器和健壮的错误处理机制。

**核心技能：**
- 使用结构体标签进行输入验证
- 自定义验证器创建
- 支持部分失败的批量操作
- 详细的错误响应
- 过滤与搜索功能

**涵盖主题：**
- 验证器包集成
- 自定义验证规则
- 错误消息格式化
- API 过滤模式
- 批量操作处理

---

### ⚡ [挑战 4：认证与会话管理](./challenge-4-authentication/)
**难度：** 高级 | **时长：** 75-90 分钟

构建一个安全的用户认证 API，支持 JWT 令牌、密码哈希和基于角色的访问控制。

**核心技能：**
- JWT 令牌生成与验证
- 使用 bcrypt 进行密码哈希
- 基于角色的访问控制
- 认证中间件
- 会话管理

**涵盖主题：**
- 用户注册与登录
- JWT 声明与验证
- 密码安全最佳实践
- 受保护路由中间件
- 管理员角色管理

---

## 为什么学习 Fiber？

**🚀 性能卓越**：基于 Fasthttp 构建，提供高性能 HTTP 处理能力

**📝 类似 Express**：对 JavaScript 开发者而言熟悉的路由与中间件模式

**🔧 功能丰富**：内置中间件、验证支持及庞大的生态系统

**🎯 生产就绪**：被多家公司用于高流量应用

## 学习路径

1. **如果你是 Fiber 或 Go 语言 Web 框架的新手，请从挑战 1 开始**
2. **如果你已掌握 Go 中的基础 HTTP 概念，可直接跳至挑战 2**
3. **挑战 3 专注于现实世界中的关注点，如验证与错误处理**
4. **挑战 4 涵盖生产环境应用的高级特性**

## 先决条件

- **基础 Go 知识**：变量、结构体、函数、包
- **HTTP 基础**：理解 HTTP 方法、状态码、头部信息
- **JSON 处理**：在 Go 中对 JSON 的基本熟悉

## 真实应用场景

这些挑战帮助你为以下项目做好准备：

- **高性能 REST API**
- **支持 WebSocket 的实时应用**
- **需要快速响应时间的微服务**
- **每秒处理数千请求的 API 网关**

## 挑战结构

每个挑战遵循一致的结构：

```
challenge-X-name/
├── README.md              # 挑战说明与要求
├── solution-template.go   # 包含 TODO 的模板文件
├── solution-template_test.go  # 全面的测试套件
├── run_tests.sh          # 测试运行脚本
├── go.mod                # 包含依赖项的 Go 模块
├── metadata.json         # 挑战元数据
├── SCOREBOARD.md         # 参与者得分表
├── hints.md              # 实现提示（如有）
├── learning.md           # 额外学习资源（如有）
└── submissions/          # 参与者提交目录
```

## 开始入门

1. **根据你的经验水平选择起始挑战**
2. **阅读挑战目录中的 README.md**
3. **在 `solution-template.go` 中实现解决方案**
4. **使用 `./run_tests.sh` 测试你的解决方案**
5. **通过 PR 提交至 submissions 目录**

## 测试你的解决方案

每个挑战都包含全面的测试套件。要测试你的解决方案，请执行：

```bash
cd packages/fiber/challenge-X-name/
./run_tests.sh
```

测试脚本将：
- 提示输入你的 GitHub 用户名
- 将你的解决方案复制到临时环境
- 对你的实现运行所有测试
- 提供详细的测试结果反馈

## 常见模式与最佳实践

### 基础应用设置
```go
app := fiber.New()

app.Get("/", func(c *fiber.Ctx) error {
    return c.JSON(fiber.Map{
        "message": "Hello, World!",
    })
})

app.Listen(":3000")
```

### 中间件使用
```go
// 内置中间件
app.Use(logger.New())
app.Use(cors.New())

// 自定义中间件
app.Use(func(c *fiber.Ctx) error {
    // 自定义逻辑
    return c.Next()
})
```

### 错误处理
```go
app.Get("/users/:id", func(c *fiber.Ctx) error {
    id := c.Params("id")
    if id == "" {
        return c.Status(400).JSON(fiber.Map{
            "error": "ID 是必需的",
        })
    }
    
    // 处理请求
    return c.JSON(response)
})
```

## 资源

- [官方 Fiber 文档](https://docs.gofiber.io/)
- [Fiber GitHub 仓库](https://github.com/gofiber/fiber)
- [Fiber 示例](https://github.com/gofiber/recipes)
- [性能基准测试](https://docs.gofiber.io/extra/benchmarks)

---

准备好使用 Fiber 构建极速 Web 应用了吗？从挑战 1 开始吧！🚀