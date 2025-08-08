# 挑战 2：中间件与请求/响应处理

使用 Fiber 构建一个**增强版博客 API**，展示高级中间件模式。

## 挑战要求

你需要实现以下中间件：

1. **自定义日志中间件** - 记录所有请求，包含耗时和请求 ID
2. **认证中间件** - 使用 API 密钥保护特定路由
3. **CORS 中间件** - 正确处理跨域请求
4. **限流中间件** - 按 IP 限制请求次数（每分钟最多 100 次）
5. **请求 ID 中间件** - 为每个请求添加唯一请求 ID
6. **错误处理中间件** - 集中化错误管理，返回一致的响应格式

## API 端点

### 公共端点
- `GET /ping` - 健康检查
- `GET /articles` - 获取所有文章（分页）
- `GET /articles/:id` - 根据 ID 获取文章

### 受保护端点（需 API 密钥：`X-API-Key` 请求头）
- `POST /articles` - 创建新文章
- `PUT /articles/:id` - 更新文章
- `DELETE /articles/:id` - 删除文章
- `GET /admin/stats` - 获取 API 使用统计信息

**有效 API 密钥：** `admin-key-123`（全部访问权限），`user-key-456`（仅读取受保护路由）

## 数据结构

```go
type Article struct {
    ID        int       `json:"id"`
    Title     string    `json:"title"`
    Content   string    `json:"content"`
    Author    string    `json:"author"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

type APIResponse struct {
    Success   bool        `json:"success"`
    Data      interface{} `json:"data,omitempty"`
    Message   string      `json:"message,omitempty"`
    Error     string      `json:"error,omitempty"`
    RequestID string      `json:"request_id,omitempty"`
}
```

## 测试要求

你的解决方案必须支持：
- 正确的中间件执行顺序
- 请求 ID 的生成与传递
- 限流策略执行（每分钟超过 100 次请求则拒绝）
- 跨域请求的 CORS 头部处理
- 受保护路由的身份验证校验
- 集中式错误处理，返回统一的响应格式
- 包含耗时信息的请求日志记录