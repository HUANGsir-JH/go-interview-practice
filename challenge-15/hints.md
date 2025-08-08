# 挑战15：OAuth2认证系统提示

## 提示1：OAuth2客户端注册与管理
从实现安全存储的客户端注册开始：
```go
type OAuth2Client struct {
    ClientID     string `json:"client_id"`
    ClientSecret string `json:"client_secret"`
    RedirectURIs []string `json:"redirect_uris"`
    Scopes       []string `json:"scopes"`
    GrantTypes   []string `json:"grant_types"`
}

type ClientStore struct {
    clients map[string]*OAuth2Client
    mutex   sync.RWMutex
}

func (cs *ClientStore) RegisterClient(redirectURIs []string, scopes []string) (*OAuth2Client, error) {
    cs.mutex.Lock()
    defer cs.mutex.Unlock()
    
    client := &OAuth2Client{
        ClientID:     generateClientID(),
        ClientSecret: generateClientSecret(),
        RedirectURIs: redirectURIs,
        Scopes:       scopes,
        GrantTypes:   []string{"authorization_code", "refresh_token"},
    }
    
    cs.clients[client.ClientID] = client
    return client, nil
}
```

## 提示2：授权端点实现
实现处理用户同意的授权端点：
```go
func (s *OAuth2Server) AuthorizeHandler(w http.ResponseWriter, r *http.Request) {
    // 解析授权请求
    authReq := &AuthorizationRequest{
        ClientID:     r.URL.Query().Get("client_id"),
        RedirectURI:  r.URL.Query().Get("redirect_uri"),
        ResponseType: r.URL.Query().Get("response_type"),
        Scope:        r.URL.Query().Get("scope"),
        State:        r.URL.Query().Get("state"),
        CodeChallenge: r.URL.Query().Get("code_challenge"),
        CodeChallengeMethod: r.URL.Query().Get("code_challenge_method"),
    }
    
    // 验证客户端和重定向URI
    client, err := s.clientStore.GetClient(authReq.ClientID)
    if err != nil {
        http.Error(w, "invalid_client", http.StatusBadRequest)
        return
    }
    
    if !contains(client.RedirectURIs, authReq.RedirectURI) {
        http.Error(w, "invalid_redirect_uri", http.StatusBadRequest)
        return
    }
    
    // 生成授权码
    authCode := generateAuthorizationCode()
    s.codeStore.StoreCode(authCode, authReq, 10*time.Minute) // 10分钟过期
    
    // 重定向并携带授权码
    redirectURL := fmt.Sprintf("%s?code=%s&state=%s", authReq.RedirectURI, authCode, authReq.State)
    http.Redirect(w, r, redirectURL, http.StatusFound)
}
```

## 提示3：支持PKCE的令牌端点
实现交换代码获取令牌的令牌端点：
```go
func (s *OAuth2Server) TokenHandler(w http.ResponseWriter, r *http.Request) {
    grantType := r.FormValue("grant_type")
    
    switch grantType {
    case "authorization_code":
        s.handleAuthorizationCodeGrant(w, r)
    case "refresh_token":
        s.handleRefreshTokenGrant(w, r)
    default:
        writeErrorResponse(w, "unsupported_grant_type", "不支持的授权类型")
    }
}

func (s *OAuth2Server) handleAuthorizationCodeGrant(w http.ResponseWriter, r *http.Request) {
    code := r.FormValue("code")
    clientID := r.FormValue("client_id")
    codeVerifier := r.FormValue("code_verifier")
    
    // 验证授权码
    authReq, err := s.codeStore.GetCode(code)
    if err != nil {
        writeErrorResponse(w, "invalid_grant", "授权码无效")
        return
    }
    
    // 如果存在，验证PKCE
    if authReq.CodeChallenge != "" {
        if !validatePKCE(authReq.CodeChallenge, authReq.CodeChallengeMethod, codeVerifier) {
            writeErrorResponse(w, "invalid_grant", "PKCE验证失败")
            return
        }
    }
    
    // 生成令牌
    accessToken := generateAccessToken()
    refreshToken := generateRefreshToken()
    
    tokenResponse := &TokenResponse{
        AccessToken:  accessToken,
        TokenType:    "Bearer",
        ExpiresIn:    3600, // 1小时
        RefreshToken: refreshToken,
        Scope:        authReq.Scope,
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(tokenResponse)
}
```

## 提示4：PKCE实现
实现代码交换证明以增强安全性：
```go
import (
    "crypto/sha256"
    "encoding/base64"
)

func generateCodeVerifier() string {
    // 生成长度为43-128字符的随机字符串
    return base64.RawURLEncoding.EncodeToString(randomBytes(32))
}

func generateCodeChallenge(verifier string) string {
    hash := sha256.Sum256([]byte(verifier))
    return base64.RawURLEncoding.EncodeToString(hash[:])
}

func validatePKCE(challenge, method, verifier string) bool {
    switch method {
    case "S256":
        expectedChallenge := generateCodeChallenge(verifier)
        return expectedChallenge == challenge
    case "plain":
        return challenge == verifier
    default:
        return false
    }
}
```

## 提示5：令牌验证与探查
实现受保护资源的令牌验证：
```go
func (s *OAuth2Server) ValidateToken(tokenString string) (*TokenInfo, error) {
    s.tokenStore.mutex.RLock()
    defer s.tokenStore.mutex.RUnlock()
    
    tokenInfo, exists := s.tokenStore.tokens[tokenString]
    if !exists {
        return nil, errors.New("令牌未找到")
    }
    
    if time.Now().After(tokenInfo.ExpiresAt) {
        delete(s.tokenStore.tokens, tokenString)
        return nil, errors.New("令牌已过期")
    }
    
    return tokenInfo, nil
}
```

## OAuth2核心概念：
- **授权码流程**：适用于Web应用的安全流程
- **PKCE**：代码交换证明，用于增强安全性
- **作用域**：定义访问令牌的权限级别
- **令牌过期**：实现正确的令牌生命周期管理
- **刷新令牌**：允许客户端获取新的访问令牌
- **安全存储**：保护客户端密钥和令牌