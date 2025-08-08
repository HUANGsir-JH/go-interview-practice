# 挑战 4：认证与会话管理

构建一个安全的 **用户认证 API**，支持 JWT 令牌、密码哈希和基于角色的访问控制。

## 挑战要求

实现具备以下端点的认证系统：

### 公共端点
- `POST /auth/register` - 带验证的用户注册
- `POST /auth/login` - 使用 JWT 令牌生成的用户登录
- `GET /health` - 公共健康检查

### 受保护端点（需 JWT）
- `GET /profile` - 获取当前用户资料
- `PUT /profile` - 更新用户资料
- `POST /auth/refresh` - 刷新 JWT 令牌

### 管理员端点（需管理员角色）
- `GET /admin/users` - 列出所有用户（仅管理员）
- `PUT /admin/users/:id/role` - 更新用户角色（仅管理员）

## 数据结构

```go
type User struct {
    ID       int    `json:"id"`
    Username string `json:"username" validate:"required,min=3,max=20"`
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"-"` // 永远不在 JSON 中返回
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
- 最小长度 8 位
- 必须包含大写字母、小写字母、数字和特殊字符
- 使用 bcrypt 哈希密码，成本为 12

### JWT 令牌安全
- 使用 HS256 算法
- 在声明中包含用户 ID、用户名和角色
- 令牌过期时间：1 小时
- 刷新令牌过期时间：7 天

### 基于角色的访问控制
- **user**：可访问自己的资料并进行更新
- **admin**：可访问所有用户数据并修改用户角色

## API 示例

**POST /auth/register**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecureP@ss123"
}
```

**POST /auth/login**
```json
{
    "username": "john_doe",
    "password": "SecureP@ss123"
}
```

**响应：**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "user",
        "active": true
    }
}
```

## 测试要求

你的解决方案必须处理：
- 带密码验证的用户注册
- 密码哈希与验证
- JWT 令牌生成与验证
- 基于角色的访问控制
- 令牌过期处理
- 安全的密码存储（绝不返回在响应中）
- 用户认证与授权
- 带验证的资料更新