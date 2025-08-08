# 挑战4：认证与会话管理提示

## 提示1：密码验证

实现强密码验证：

```go
import "regexp"

func validatePassword(password string) bool {
    if len(password) < 8 {
        return false
    }
    
    // 检查至少包含一个大写字母
    hasUpper, _ := regexp.MatchString(`[A-Z]`, password)
    // 检查至少包含一个小写字母
    hasLower, _ := regexp.MatchString(`[a-z]`, password)
    // 检查至少包含一个数字
    hasDigit, _ := regexp.MatchString(`\d`, password)
    // 检查至少包含一个特殊字符
    hasSpecial, _ := regexp.MatchString(`[!@#$%^&*(),.?":{}|<>]`, password)
    
    return hasUpper && hasLower && hasDigit && hasSpecial
}
```

## 提示2：使用bcrypt进行密码哈希

使用bcrypt进行安全的密码哈希：

```go
import "golang.org/x/crypto/bcrypt"

func hashPassword(password string) (string, error) {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    if err != nil {
        return "", err
    }
    return string(hash), nil
}

func verifyPassword(password, hash string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
    return err == nil
}
```

## 提示3：JWT令牌生成

使用自定义声明创建JWT令牌：

```go
import "github.com/golang-jwt/jwt/v5"

func generateJWT(user User) (string, error) {
    claims := jwt.MapClaims{
        "user_id":  user.ID,
        "username": user.Username,
        "role":     user.Role,
        "exp":      time.Now().Add(time.Hour * 1).Unix(),
        "iat":      time.Now().Unix(),
    }
    
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(jwtSecret)
}
```

## 提示4：JWT令牌验证

解析并验证JWT令牌：

```go
func validateJWT(tokenString string) (*JWTClaims, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("不支持的签名方法")
        }
        return jwtSecret, nil
    })
    
    if err != nil {
        return nil, err
    }
    
    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        return &JWTClaims{
            UserID:   int(claims["user_id"].(float64)),
            Username: claims["username"].(string),
            Role:     claims["role"].(string),
            Exp:      int64(claims["exp"].(float64)),
        }, nil
    }
    
    return nil, fmt.Errorf("无效的令牌")
}
```

## 提示5：JWT中间件

从请求中提取并验证令牌：

```go
func jwtMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        authHeader := c.Get("Authorization")
        if authHeader == "" {
            return c.Status(401).JSON(fiber.Map{
                "success": false,
                "message": "需要授权头",
            })
        }
        
        // 预期格式："Bearer <token>"
        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            return c.Status(401).JSON(fiber.Map{
                "success": false,
                "message": "无效的授权头格式",
            })
        }
        
        claims, err := validateJWT(parts[1])
        if err != nil {
            return c.Status(401).JSON(fiber.Map{
                "success": false,
                "message": "令牌无效或已过期",
            })
        }
        
        // 将声明存储在上下文中供处理器使用
        c.Locals("user_claims", claims)
        return c.Next()
    }
}
```

## 提示6：基于角色的访问控制

检查用户角色以保护管理员端点：

```go
func adminMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        claims := c.Locals("user_claims").(*JWTClaims)
        
        if claims.Role != "admin" {
            return c.Status(403).JSON(fiber.Map{
                "success": false,
                "message": "需要管理员权限",
            })
        }
        
        return c.Next()
    }
}
```

## 提示7：注册处理器

处理用户注册并进行验证：

```go
func registerHandler(c *fiber.Ctx) error {
    var req RegisterRequest
    if err := c.BodyParser(&req); err != nil {
        return c.Status(400).JSON(AuthResponse{
            Success: false,
            Message: "请求格式无效",
        })
    }
    
    // 验证输入
    if err := validate.Struct(req); err != nil {
        return c.Status(400).JSON(AuthResponse{
            Success: false,
            Message: "验证失败",
        })
    }
    
    // 检查用户名是否已存在
    if _, exists := findUserByUsername(req.Username); exists {
        return c.Status(409).JSON(AuthResponse{
            Success: false,
            Message: "用户名已存在",
        })
    }
    
    // 检查邮箱是否已注册
    if _, exists := findUserByEmail(req.Email); exists {
        return c.Status(409).JSON(AuthResponse{
            Success: false,
            Message: "邮箱已被注册",
        })
    }
    
    // 验证密码强度
    if !validatePassword(req.Password) {
        return c.Status(400).JSON(AuthResponse{
            Success: false,
            Message: "密码必须包含大写字母、小写字母、数字和特殊字符",
        })
    }
    
    // 哈希密码
    hashedPassword, err := hashPassword(req.Password)
    if err != nil {
        return c.Status(500).JSON(AuthResponse{
            Success: false,
            Message: "密码处理失败",
        })
    }
    
    // 创建用户
    user := User{
        ID:       nextUserID,
        Username: req.Username,
        Email:    req.Email,
        Password: hashedPassword,
        Role:     "user",
        Active:   true,
    }
    
    users = append(users, user)
    nextUserID++
    
    return c.Status(201).JSON(AuthResponse{
        Success: true,
        User:    user,
        Message: "用户注册成功",
    })
}
```

## 提示8：登录处理器

认证用户并返回JWT令牌：

```go
func loginHandler(c *fiber.Ctx) error {
    var req LoginRequest
    if err := c.BodyParser(&req); err != nil {
        return c.Status(400).JSON(AuthResponse{
            Success: false,
            Message: "请求格式无效",
        })
    }
    
    // 查找用户
    user, _ := findUserByUsername(req.Username)
    if user == nil {
        return c.Status(401).JSON(AuthResponse{
            Success: false,
            Message: "凭证无效",
        })
    }
    
    // 验证密码
    if !verifyPassword(req.Password, user.Password) {
        return c.Status(401).JSON(AuthResponse{
            Success: false,
            Message: "凭证无效",
        })
    }
    
    // 检查用户是否激活
    if !user.Active {
        return c.Status(401).JSON(AuthResponse{
            Success: false,
            Message: "账户已被禁用",
        })
    }
    
    // 生成JWT令牌
    token, err := generateJWT(*user)
    if err != nil {
        return c.Status(500).JSON(AuthResponse{
            Success: false,
            Message: "无法生成令牌",
        })
    }
    
    return c.JSON(AuthResponse{
        Success: true,
        Token:   token,
        User:    *user,
        Message: "登录成功",
    })
}
```

## 提示9：受保护路由模式

使用中间件保护路由：

```go
// 设置路由组
app := fiber.New()

// 公共路由
app.Post("/auth/register", registerHandler)
app.Post("/auth/login", loginHandler)
app.Get("/health", healthHandler)

// 受保护路由（需要有效的JWT）
protected := app.Group("/", jwtMiddleware())
protected.Get("/profile", getProfileHandler)
protected.Put("/profile", updateProfileHandler)
protected.Post("/auth/refresh", refreshTokenHandler)

// 管理员路由（需要管理员角色）
admin := app.Group("/admin", jwtMiddleware(), adminMiddleware())
admin.Get("/users", listUsersHandler)
admin.Put("/users/:id/role", updateUserRoleHandler)
```