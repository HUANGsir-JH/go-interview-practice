# 挑战 1：基础路由

使用 Fiber 构建一个简单的 **任务管理 API**，包含基础的 HTTP 路由和请求处理。

## 挑战要求

实现一个用于管理任务的 REST API，包含以下端点：

- `GET /ping` - 健康检查端点（返回 "pong"）
- `GET /tasks` - 获取所有任务
- `GET /tasks/:id` - 根据 ID 获取任务
- `POST /tasks` - 创建新任务
- `PUT /tasks/:id` - 更新现有任务
- `DELETE /tasks/:id` - 删除任务

## 数据结构

```go
type Task struct {
    ID          int    `json:"id"`
    Title       string `json:"title"`
    Description string `json:"description"`
    Completed   bool   `json:"completed"`
}
```

## 请求/响应示例

**GET /tasks**
```json
[
    {
        "id": 1,
        "title": "学习 Go",
        "description": "完成 Go 教程",
        "completed": false
    }
]
```

**POST /tasks**（请求体）
```json
{
    "title": "新任务",
    "description": "任务描述",
    "completed": false
}
```

## 测试要求

你的实现必须通过所有提供的测试，这些测试验证：

- ✅ 正确的 HTTP 方法和路由
- ✅ 正确的 JSON 请求/响应处理
- ✅ 路径参数提取
- ✅ 内存中数据持久化
- ✅ 无效请求的错误处理
- ✅ 适当的 HTTP 状态码

## 实现说明

- 使用 Fiber 内置的 JSON 处理功能，通过 `c.JSON()`
- 使用 `c.Params()` 提取路径参数
- 使用 `c.BodyParser()` 解析 JSON 请求体
- 将任务存储在内存中（切片或映射）
- 返回适当的 HTTP 状态码

## 开始步骤

1. 查看 `solution-template.go` 文件
2. 实现 TODO 部分
3. 使用 `./run_tests.sh` 运行测试
4. 迭代直到所有测试通过

## 成功标准

- 所有测试通过
- 代码清晰易读
- 正确的错误处理
- 符合 RESTful 设计规范
- 高效的内存存储