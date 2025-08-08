# 挑战 4：认证与会话管理

构建一个安全的 **用户认证 API**，支持 JWT 令牌、密码哈希和基于角色的访问控制。

## 挑战要求

实现具备以下端点的认证系统：

### 公共端点
- `POST /auth/register` - 用户注册并进行验证
- `POST /auth/login` - 用户登录并生成 JWT 令牌
- `GET /health` - 公共健康检查

### 受保护端点（需要 JWT）
- `GET /profile` - 获取当前用户资料
- `PUT /profile` - 更新用户资料
- `POST /auth/refresh` - 刷新 JWT 令牌

### 管理员端点（需要管理员角色）
- `GET /admin/users` - 列出所有用户（仅管理员）
- `PUT /admin/users/:id/role` - 更新用户角色（仅管理员）

## 数据结构

```go
type User struct {
    ID       int    `json:"id"`
    Username string `json:"username" binding:"required,min=3,max=20"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"-"` // 不在 JSON 中返回
    Role     string `json:"role"` // "user" 或 "admin"
    Active   bool   `json:"active"`
}

type AuthResponse struct {
    Success bool   `json:"success"`
    Token   string `json:"token,omitempty"`
    User    User   `json:"user,omitempty"`
    Message string `json:"message,omitempty"`
}
```

## 安全要求

### 密码安全
- 最少 8 个字符
- 必须包含大写字母、小写字母、数字和特殊字符
- 使用 bcrypt 哈希（成本因子 12）

### JWT 实现
- 使用 HS256 算法
- 在声明中包含用户 ID 和角色
- 有效期为 24 小时
- 实现正确的令牌验证中间件

### 基于角色的访问控制
- 普通用户：仅可访问个人资料相关端点
- 管理员：可访问所有端点，包括用户管理功能

## 测试要求

你的解决方案必须通过以下测试：
- 带密码验证的用户注册
- 密码哈希（bcrypt 验证）
- 使用正确凭证的用户登录
- JWT 令牌生成与验证
- 受保护端点的访问控制
- 基于角色的授权（管理员 vs 普通用户）
- 令牌刷新功能
- 无效凭证情况下的正确错误处理