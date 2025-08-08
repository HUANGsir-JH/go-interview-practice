# 学习：认证与会话管理

## 🌟 **什么是认证？**

认证是验证用户或系统身份的过程。它回答了“你是谁？”这个问题，是保护Web应用程序的基础。

### **认证 vs 授权**
- **认证**：验证身份（“你是谁？”）
- **授权**：确定权限（“你能做什么？”）

## 🔐 **密码安全**

### **使用 bcrypt 进行密码哈希**
切勿存储明文密码。请使用 bcrypt 进行安全哈希：

```go
import "golang.org/x/crypto/bcrypt"

func hashPassword(password string) (string, error) {
    // 12 的成本值在安全性和性能之间提供了良好的平衡
    hash, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    return string(hash), err
}

func verifyPassword(password, hash string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
    return err == nil
}
```

### **密码强度要求**
实施强密码策略：

```go
func validatePassword(password string) []string {
    var errors []string
    
    if len(password) < 8 {
        errors = append(errors, "密码必须至少包含8个字符")
    }
    
    if !regexp.MustCompile(`[A-Z]`).MatchString(password) {
        errors = append(errors, "密码必须包含大写字母")
    }
    
    if !regexp.MustCompile(`[a-z]`).MatchString(password) {
        errors = append(errors, "密码必须包含小写字母")
    }
    
    if !regexp.MustCompile(`\d`).MatchString(password) {
        errors = append(errors, "密码必须包含数字")
    }
    
    if !regexp.MustCompile(`[!@#$%^&*]`).MatchString(password) {
        errors = append(errors, "密码必须包含特殊字符")
    }
    
    return errors
}
```

## 🎫 **JWT（JSON Web Tokens）**

JWT 是一种无状态的认证方法，将用户信息编码在令牌中。

### **JWT 结构**
JWT 由三部分组成，用点号分隔：
- **头部**：算法和令牌类型
- **载荷**：声明（用户数据）
- **签名**：验证签名

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### **生成 JWT 令牌**
```go
import "github.com/golang-jwt/jwt/v5"

type Claims struct {
    UserID   int    `json:"user_id"`
    Username string `json:"username"`
    Role     string `json:"role"`
    jwt.RegisteredClaims
}

func generateJWT(user User, secret []byte) (string, error) {
    claims := &Claims{
        UserID:   user.ID,
        Username: user.Username,
        Role:     user.Role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            NotBefore: jwt.NewNumericDate(time.Now()),
            Issuer:    "your-app-name",
            Subject:   strconv.Itoa(user.ID),
        },
    }
    
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}
```

### **验证 JWT 令牌**
```go
func validateJWT(tokenString string, secret []byte) (*Claims, error) {
    claims := &Claims{}
    
    token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
        // 验证签名方法
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("意外的签名方法: %v", token.Header["alg"])
        }
        return secret, nil
    })
    
    if err != nil {
        return nil, err
    }
    
    if !token.Valid {
        return nil, fmt.Errorf("无效的令牌")
    }
    
    return claims, nil
}
```

## 🛡️ **认证中间件**

### **JWT 认证中间件**
```go
func jwtMiddleware(secret []byte) fiber.Handler {
    return func(c *fiber.Ctx) error {
        // 从 Authorization 头部提取令牌
        authHeader := c.Get("Authorization")
        if authHeader == "" {
            return c.Status(401).JSON(fiber.Map{
                "error": "缺少授权头",
            })
        }
        
        // 解析 "Bearer <token>" 格式
        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            return c.Status(401).JSON(fiber.Map{
                "error": "无效的授权头格式",
            })
        }
        
        // 验证令牌
        claims, err := validateJWT(parts[1], secret)
        if err != nil {
            return c.Status(401).JSON(fiber.Map{
                "error": "无效或过期的令牌",
            })
        }
        
        // 将用户信息存入上下文
        c.Locals("user_id", claims.UserID)
        c.Locals("username", claims.Username)
        c.Locals("role", claims.Role)
        
        return c.Next()
    }
}
```

### **基于角色的访问控制**
```go
func requireRole(requiredRole string) fiber.Handler {
    return func(c *fiber.Ctx) error {
        userRole := c.Locals("role").(string)
        
        if userRole != requiredRole {
            return c.Status(403).JSON(fiber.Map{
                "error": "权限不足",
            })
        }
        
        return c.Next()
    }
}

// 使用示例
admin := app.Group("/admin", jwtMiddleware(secret), requireRole("admin"))
```

## 🔄 **会话管理**

### **令牌刷新模式**
实现令牌刷新以提高安全性：

```go
type TokenPair struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
}

func generateTokenPair(user User) (*TokenPair, error) {
    // 短时访问令牌（15分钟）
    accessToken, err := generateJWT(user, 15*time.Minute)
    if err != nil {
        return nil, err
    }
    
    // 长时刷新令牌（7天）
    refreshToken, err := generateRefreshToken(user, 7*24*time.Hour)
    if err != nil {
        return nil, err
    }
    
    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
    }, nil
}
```

### **令牌黑名单**
维护被撤销令牌的黑名单：

```go
type TokenBlacklist struct {
    mu     sync.RWMutex
    tokens map[string]time.Time
}

func (tb *TokenBlacklist) Add(tokenID string, expiry time.Time) {
    tb.mu.Lock()
    defer tb.mu.Unlock()
    tb.tokens[tokenID] = expiry
}

func (tb *TokenBlacklist) IsBlacklisted(tokenID string) bool {
    tb.mu.RLock()
    defer tb.mu.RUnlock()
    
    expiry, exists := tb.tokens[tokenID]
    if !exists {
        return false
    }
    
    // 清理过期条目
    if time.Now().After(expiry) {
        delete(tb.tokens, tokenID)
        return false
    }
    
    return true
}
```

## 👤 **用户管理模式**

### **用户注册**
```go
func registerUser(req RegisterRequest) (*User, error) {
    // 验证输入
    if err := validateRegistration(req); err != nil {
        return nil, err
    }
    
    // 检查用户是否存在
    if userExists(req.Username, req.Email) {
        return nil, errors.New("用户已存在")
    }
    
    // 哈希密码
    hashedPassword, err := hashPassword(req.Password)
    if err != nil {
        return nil, err
    }
    
    // 创建用户
    user := &User{
        ID:       generateUserID(),
        Username: req.Username,
        Email:    req.Email,
        Password: hashedPassword,
        Role:     "user",
        Active:   true,
        CreatedAt: time.Now(),
    }
    
    // 保存到数据库/存储
    if err := saveUser(user); err != nil {
        return nil, err
    }
    
    return user, nil
}
```

### **用户登录**
```go
func loginUser(req LoginRequest) (*AuthResponse, error) {
    // 查找用户
    user, err := findUserByUsername(req.Username)
    if err != nil {
        return nil, errors.New("无效凭据")
    }
    
    // 验证密码
    if !verifyPassword(req.Password, user.Password) {
        return nil, errors.New("无效凭据")
    }
    
    // 检查账户是否激活
    if !user.Active {
        return nil, errors.New("账户已被禁用");
    }
    
    // 生成令牌
    tokenPair, err := generateTokenPair(*user)
    if err != nil {
        return nil, err
    }
    
    return &AuthResponse{
        User:         *user,
        AccessToken:  tokenPair.AccessToken,
        RefreshToken: tokenPair.RefreshToken,
    }, nil
}
```

## 🔒 **安全最佳实践**

### **1. 安全的令牌存储**
- 将 JWT 密钥存储在环境变量中
- 使用强且随机生成的密钥
- 定期轮换密钥

```go
func getJWTSecret() []byte {
    secret := os.Getenv("JWT_SECRET")
    if secret == "" {
        log.Fatal("JWT_SECRET 环境变量是必需的")
    }
    return []byte(secret)
}
```

### **2. 速率限制**
防止暴力破解攻击：

```go
func loginRateLimit() fiber.Handler {
    // 每个IP每分钟允许5次登录尝试
    return limiter.New(limiter.Config{
        Max:        5,
        Expiration: 1 * time.Minute,
        KeyGenerator: func(c *fiber.Ctx) string {
            return c.IP()
        },
    })
}
```

### **3. 输入验证**
始终验证并清理输入：

```go
func validateLoginRequest(req LoginRequest) error {
    if req.Username == "" {
        return errors.New("用户名是必需的")
    }
    
    if req.Password == "" {
        return errors.New("密码是必需的")
    }
    
    // 清理用户名
    req.Username = strings.TrimSpace(req.Username)
    
    return nil
}
```

### **4. 仅限 HTTPS**
生产环境中始终使用 HTTPS：

```go
app := fiber.New(fiber.Config{
    // 强制使用 HTTPS
    EnableTrustedProxyCheck: true,
    TrustedProxies: []string{"127.0.0.1"},
})

// 添加安全头
app.Use(func(c *fiber.Ctx) error {
    c.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return c.Next()
})
```

## 🧪 **测试认证**

### **测试 JWT 函数**
```go
func TestJWTGeneration(t *testing.T) {
    user := User{
        ID:       1,
        Username: "testuser",
        Role:     "user",
    }
    
    secret := []byte("test-secret")
    
    token, err := generateJWT(user, secret)
    assert.NoError(t, err)
    assert.NotEmpty(t, token)
    
    // 验证令牌
    claims, err := validateJWT(token, secret)
    assert.NoError(t, err)
    assert.Equal(t, user.ID, claims.UserID)
    assert.Equal(t, user.Username, claims.Username)
}
```

### **测试受保护端点**
```go
func TestProtectedEndpoint(t *testing.T) {
    app := setupTestApp()
    
    // 测试无令牌情况
    req := httptest.NewRequest("GET", "/profile", nil)
    resp, _ := app.Test(req)
    assert.Equal(t, 401, resp.StatusCode)
    
    // 测试有效令牌
    token := generateTestToken(t)
    req = httptest.NewRequest("GET", "/profile", nil)
    req.Header.Set("Authorization", "Bearer "+token)
    resp, _ = app.Test(req)
    assert.Equal(t, 200, resp.StatusCode)
}
```

## 🎯 **最佳实践总结**

1. **永远不要存储明文密码**
2. **使用强密码要求**
3. **实现正确的 JWT 验证**
4. **生产环境中使用 HTTPS**
5. **实现速率限制**
6. **验证并清理所有输入**
7. **使用环境变量存储密钥**
8. **实现适当的错误处理**
9. **彻底测试认证逻辑**
10. **遵循最小权限原则**

## 📚 **下一步**

掌握认证后：
1. **OAuth2 集成** - 第三方认证
2. **多因素认证** - 增强安全性
3. **会话存储** - Redis/数据库会话
4. **审计日志** - 跟踪认证事件