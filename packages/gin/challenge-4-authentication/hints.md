# 挑战 4 提示：认证与会话管理

## 提示 1：密码强度验证

实现全面的密码强度检查：

```go
func isStrongPassword(password string) bool {
    if len(password) < 8 {
        return false
    }
    
    hasUpper := false
    hasLower := false
    hasDigit := false
    hasSpecial := false
    
    for _, char := range password {
        switch {
        case 'A' <= char && char <= 'Z':
            hasUpper = true
        case 'a' <= char && char <= 'z':
            hasLower = true
        case '0' <= char && char <= '9':
            hasDigit = true
        default:
            hasSpecial = true
        }
    }
    
    return hasUpper && hasLower && hasDigit && hasSpecial
}
```

## 提示 2：使用 Bcrypt 进行密码哈希

使用 bcrypt 实现安全的密码哈希：

```go
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

## 提示 3：JWT 令牌生成

使用适当的声明生成安全的 JWT 令牌：

```go
func generateTokens(userID int, username, role string) (*TokenResponse, error) {
    // 访问令牌
    accessClaims := &JWTClaims{
        UserID:   userID,
        Username: username,
        Role:     role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(accessTokenTTL)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "your-app",
        },
    }
    
    accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims)
    accessTokenString, err := accessToken.SignedString(jwtSecret)
    if err != nil {
        return nil, err
    }
    
    // 刷新令牌
    refreshToken, err := generateRandomToken()
    if err != nil {
        return nil, err
    }
    
    // 存储刷新令牌
    refreshTokens[refreshToken] = userID
    
    return &TokenResponse{
        AccessToken:  accessTokenString,
        RefreshToken: refreshToken,
        TokenType:    "Bearer",
        ExpiresIn:    int64(accessTokenTTL.Seconds()),
        ExpiresAt:    time.Now().Add(accessTokenTTL),
    }, nil
}
```

## 提示 4：JWT 令牌验证

验证并解析 JWT 令牌：

```go
func validateToken(tokenString string) (*JWTClaims, error) {
    // 检查令牌是否在黑名单中
    if blacklistedTokens[tokenString] {
        return nil, errors.New("令牌已被列入黑名单")
    }
    
    token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
        return jwtSecret, nil
    })
    
    if err != nil {
        return nil, err
    }
    
    if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
        return claims, nil
    }
    
    return nil, errors.New("无效的令牌")
}
```

## 提示 5：认证中间件

创建中间件以保护路由：

```go
func authMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(401, APIResponse{
                Success: false,
                Error:   "需要授权头",
            })
            c.Abort()
            return
        }
        
        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        claims, err := validateToken(tokenString)
        if err != nil {
            c.JSON(401, APIResponse{
                Success: false,
                Error:   "无效的令牌",
            })
            c.Abort()
            return
        }
        
        // 将用户信息设置到上下文中
        c.Set("userID", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("role", claims.Role)
        c.Next()
    }
}
```

## 提示 6：基于角色的授权

实现基于角色的访问控制：

```go
func requireRole(roles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole, exists := c.Get("role")
        if !exists {
            c.JSON(401, APIResponse{
                Success: false,
                Error:   "未授权",
            })
            c.Abort()
            return
        }
        
        roleStr := userRole.(string)
        for _, allowedRole := range roles {
            if roleStr == allowedRole {
                c.Next()
                return
            }
        }
        
        c.JSON(403, APIResponse{
            Success: false,
            Error:   "权限不足",
        })
        c.Abort()
    }
}
```

## 提示 7：账户锁定管理

处理登录失败尝试和账户锁定：

```go
func recordFailedAttempt(user *User) {
    user.FailedAttempts++
    if user.FailedAttempts >= maxFailedAttempts {
        lockUntil := time.Now().Add(lockoutDuration)
        user.LockedUntil = &lockUntil
    }
}

func isAccountLocked(user *User) bool {
    if user.LockedUntil == nil {
        return false
    }
    return time.Now().Before(*user.LockedUntil)
}

func resetFailedAttempts(user *User) {
    user.FailedAttempts = 0
    user.LockedUntil = nil
}
```

## 提示 8：安全的令牌登出

实现通过令牌黑名单机制的安全登出：

```go
func logout(c *gin.Context) {
    authHeader := c.GetHeader("Authorization")
    if authHeader == "" {
        c.JSON(401, APIResponse{
            Success: false,
            Error:   "需要授权头",
        })
        return
    }
    
    tokenString := strings.TrimPrefix(authHeader, "Bearer ")
    
    // 将令牌加入黑名单
    blacklistedTokens[tokenString] = true
    
    // 如果提供了刷新令牌，则删除
    var req struct {
        RefreshToken string `json:"refresh_token,omitempty"`
    }
    c.ShouldBindJSON(&req)
    
    if req.RefreshToken != "" {
        delete(refreshTokens, req.RefreshToken)
    }
    
    c.JSON(200, APIResponse{
        Success: true,
        Message: "登出成功",
    })
}
```