# 挑战 1：基础路由

使用 Gin 构建一个简单的 **用户管理 API**，包含基础的 HTTP 路由和请求处理。

## 挑战要求

实现一个用于管理用户的 REST API，包含以下端点：

- `GET /users` - 获取所有用户
- `GET /users/:id` - 根据 ID 获取用户
- `POST /users` - 创建新用户
- `PUT /users/:id` - 更新现有用户
- `DELETE /users/:id` - 删除用户
- `GET /users/search` - 根据姓名搜索用户

## 数据结构

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

type Response struct {
    Success bool        `json:"success"`
    Data    interface{} `json:"data,omitempty"`
    Message string      `json:"message,omitempty"`
    Error   string      `json:"error,omitempty"`
    Code    int         `json:"code,omitempty"`
}
```

## 请求/响应示例

**GET /users**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
    ]
}
```

**POST /users**（请求体）
```json
{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "age": 28
}
```

## 测试要求

你的解决方案必须通过以下测试：
- 获取所有用户返回正确的响应结构
- 根据 ID 获取用户返回正确用户或 404
- 创建用户添加新用户并自增 ID
- 更新用户修改现有用户或返回 404
- 删除用户移除用户或返回 404
- 根据姓名搜索用户（不区分大小写）
- 所有操作均返回正确的 HTTP 状态码和响应格式