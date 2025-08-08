# OAuth2 认证系统学习资料

## OAuth2 概述

OAuth 2.0 是一种授权框架，允许第三方应用程序在代表资源所有者或以自身名义的情况下，有限地访问 HTTP 服务。

### 核心概念

- **资源所有者**：拥有数据的用户（例如，在照片分享网站上有照片的用户）
- **客户端**：希望访问用户数据的第三方应用程序
- **授权服务器**：对资源所有者进行身份验证并颁发访问令牌的服务器
- **资源服务器**：托管受保护资源的服务器（可以与授权服务器相同）
- **访问令牌**：客户端用于访问受保护资源的凭证
- **刷新令牌**：在访问令牌过期时获取新访问令牌的凭证

### OAuth2 流程

OAuth 2.0 定义了多种授权类型或流程，适用于不同的使用场景：

1. **授权码**：适用于服务器端 Web 应用程序
2. **隐式**：适用于浏览器或移动应用（安全性较低，现已不推荐）
3. **资源所有者密码凭证**：适用于可信的应用程序
4. **客户端凭证**：用于应用程序访问（无需用户参与）
5. **刷新令牌**：在不重新授权的情况下获取新的访问令牌
6. **设备码**：适用于输入能力受限的设备

## 授权码流程

授权码流程是最安全且最常用的流程。其工作方式如下：

1. 客户端将用户重定向到授权服务器，携带其客户端 ID、请求的作用域和重定向 URI
2. 用户进行身份验证并授予权限
3. 授权服务器将用户重定向回客户端，并附带一个授权码
4. 客户端用授权码换取访问令牌和刷新令牌
5. 客户端使用访问令牌访问受保护的资源

```
+----------+
| Resource |
|   Owner  |
+----------+
     ^
     |
    (B)
     |
+----|-----+          Client Identifier      +---------------+
|         -+----(A)-- & Redirection URI ---->|               |
|  Client  |                                  | Authorization |
|          |<---(C)-- Authorization Code ----|    Server     |
|          |                                  |               |
|          |----(D)-- Authorization Code ---->|               |
|          |          & Redirection URI       |               |
|          |                                  |               |
|          |<---(E)----- Access Token -------|               |
+-----------+      (w/ Optional Refresh Token)  +---------------+
```

## PKCE（代码交换的证明密钥）

PKCE（发音为 "pixy"）是授权码流程的一个扩展，为公共客户端（如移动应用或单页应用）提供额外的安全性。其工作方式如下：

1. 客户端创建一个代码验证器（一个随机字符串）
2. 客户端使用转换方法（通常为 SHA-256）从代码验证器生成代码挑战
3. 客户端在授权请求中包含代码挑战和挑战方法
4. 在交换授权码时，客户端包含原始的代码验证器
5. 授权服务器对代码验证器进行转换，并将其与存储的代码挑战进行比较

```go
// 创建代码验证器
codeVerifier, _ := GenerateRandomString(64)

// 使用 S256 方法创建代码挑战
h := sha256.New()
h.Write([]byte(codeVerifier))
codeChallenge := base64.RawURLEncoding.EncodeToString(h.Sum(nil))
```

## 访问令牌

访问令牌是用于访问受保护资源的凭证。它们可以有不同格式：

1. **不透明令牌**：随机字符串，资源服务器必须通过授权服务器进行验证
2. **JWT 令牌**：包含认证和授权信息声明的 JSON Web Token

```go
// 示例 JWT 令牌
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

## 刷新令牌

刷新令牌是用于在访问令牌过期后获取新访问令牌的凭证。它们通常比访问令牌具有更长的有效期，但更为敏感，因为它们可长期授予访问权限。

```go
// 使用刷新令牌获取新的访问令牌
form := url.Values{}
form.Add("grant_type", "refresh_token")
form.Add("refresh_token", refreshToken)
form.Add("client_id", clientID)
form.Add("client_secret", clientSecret)

resp, err := http.PostForm(tokenEndpoint, form)
```

## 作用域

作用域定义了客户端请求的具体访问权限。

```
带作用域的授权请求：
GET /authorize?response_type=code&client_id=s6BhdRkqt3&state=xyz
    &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb
    &scope=read write email
```

## 令牌存储

访问令牌和刷新令牌应安全存储：

- **服务器端应用**：存储在安全数据库中
- **基于浏览器的应用**：将访问令牌存储在内存中，刷新令牌存储在 HTTP-only 安全 Cookie 中
- **移动应用**：使用平台的安全存储（iOS 上的 Keychain，Android 上的 KeyStore）

## 令牌验证

在验证令牌时，应检查：

1. 令牌签名（针对 JWT 令牌）
2. 令牌过期时间
3. 令牌签发者
4. 令牌受众
5. 令牌作用域

```go
// 验证令牌
token, err := server.ValidateToken(tokenString)
if err != nil {
    // 处理无效令牌
    return
}

// 检查令牌是否包含所需作用域
if !containsScope(token.Scopes, requiredScope) {
    // 处理作用域不足
    return
}
```

## 错误处理

OAuth2 定义了标准的错误响应：

- `invalid_request`：请求缺少参数或格式错误
- `invalid_client`：客户端身份验证失败
- `invalid_grant`：授权许可无效或已过期
- `unauthorized_client`：客户端未被授权使用此授权类型
- `unsupported_grant_type`：授权服务器不支持此授权类型
- `invalid_scope`：请求的作用域无效或未知

```json
{
  "error": "invalid_client",
  "error_description": "Client authentication failed"
}
```

## 安全注意事项

1. **使用 HTTPS**：所有 OAuth 2.0 通信都应通过 TLS 进行
2. **验证重定向 URI**：仅允许重定向到预先注册的 URI
3. **使用 PKCE**：所有客户端，尤其是公共客户端
4. **短生命周期访问令牌**：限制访问令牌的有效期
5. **验证状态参数**：防止 CSRF 攻击
6. **安全存储令牌**：根据客户端类型安全存储令牌
7. **令牌撤销**：在令牌泄露时实现令牌撤销

## JWT 结构与验证

JWT 令牌由三部分组成：

1. **头部**：标识用于生成签名的算法
2. **载荷**：包含声明
3. **签名**：确保令牌未被篡改

```go
// JWT 头部
{
  "alg": "HS256",
  "typ": "JWT"
}

// JWT 载荷
{
  "sub": "1234567890", // 主体（用户 ID）
  "name": "John Doe",
  "iat": 1516239022,   // 签发时间
  "exp": 1516242622,   // 过期时间
  "aud": "my-api",     // 受众
  "iss": "auth-server" // 签发者
}
```

## Go 中的 OAuth2

以下是一些在 Go 中实现 OAuth2 的有用库：

- `golang.org/x/oauth2`：客户端 OAuth2 实现
- `github.com/go-oauth2/oauth2`：服务器端 OAuth2 实现
- `github.com/golang-jwt/jwt`：JWT 实现

```go
// 使用 golang.org/x/oauth2 实现客户端 OAuth2
import "golang.org/x/oauth2"

conf := &oauth2.Config{
    ClientID:     "client-id",
    ClientSecret: "client-secret",
    Scopes:       []string{"read", "write"},
    RedirectURL:  "http://localhost:8080/callback",
    Endpoint: oauth2.Endpoint{
        AuthURL:  "https://provider.com/o/oauth2/auth",
        TokenURL: "https://provider.com/o/oauth2/token",
    },
}

// 生成授权 URL
url := conf.AuthCodeURL("state-token", oauth2.AccessTypeOffline)

// 用授权码交换令牌
token, err := conf.Exchange(ctx, code)
```

## OpenID Connect

OpenID Connect (OIDC) 是建立在 OAuth 2.0 之上的身份层。它允许客户端验证最终用户的 identity 并获取基本的个人资料信息。

OIDC 增加了：

1. **ID 令牌**：包含用户身份信息的 JWT
2. **UserInfo 端点**：用于获取更多用户信息
3. **标准声明**：用于用户信息，如姓名、邮箱等

```json
// 示例 ID 令牌载荷
{
  "iss": "https://server.example.com",
  "sub": "24400320",
  "aud": "s6BhdRkqt3",
  "exp": 1311281970,
  "iat": 1311280970,
  "name": "Jane Doe",
  "email": "janedoe@example.com"
}
```

## 最佳实践

1. **遵循规范**：正确实现 OAuth2 规范
2. **使用 PKCE**：所有客户端，即使保密的也应使用
3. **短生命周期令牌**：保持访问令牌短期有效（< 1 小时）
4. **轮换刷新令牌**：在刷新访问令牌时发放新的刷新令牌
5. **实现令牌撤销**：允许用户撤销访问权限
6. **验证所有参数**：包括重定向 URI 和作用域
7. **使用标准错误码**：遵循 OAuth2 错误响应格式
8. **记录认证事件**：记录所有令牌发放和使用情况以供审计
9. **测试安全性**：在测试套件中包含安全测试
10. **保持更新**：及时更新依赖项以获取安全补丁