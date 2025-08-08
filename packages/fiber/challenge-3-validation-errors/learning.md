# 学习：输入验证与错误处理

## 🌟 **什么是输入验证？**

输入验证确保API接收到的数据在处理前符合特定标准。它是防范不良数据、安全漏洞和应用崩溃的第一道防线。

### **为什么要进行输入验证？**
- **安全性**：防止注入攻击和恶意数据
- **数据完整性**：确保数据满足业务需求
- **用户体验**：对无效输入提供清晰反馈
- **系统稳定性**：防止因意外数据导致的崩溃

## 🛠️ **Fiber中的验证**

Fiber不包含内置的验证功能，但可以很好地与`validator`包集成：

```go
import "github.com/go-playground/validator/v10"

type User struct {
    Name  string `json:"name" validate:"required,min=2,max=50"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age" validate:"gte=0,lte=120"`
}
```

## 📏 **内置验证标签**

### **必填字段**
```go
type Product struct {
    Name string `validate:"required"`        // 必须存在
    SKU  string `validate:"required,min=5"`  // 必填且最小长度
}
```

### **字符串验证**
```go
type User struct {
    Username string `validate:"min=3,max=20"`           // 长度限制
    Email    string `validate:"email"`                  // 邮箱格式
    Website  string `validate:"url"`                    // URL格式
    Phone    string `validate:"e164"`                   // 电话号码格式
}
```

### **数值验证**
```go
type Product struct {
    Price    float64 `validate:"gt=0"`          // 大于0
    Quantity int     `validate:"gte=0,lte=1000"` // 范围：0-1000
    Rating   float64 `validate:"min=1,max=5"`   // 评分范围
}
```

### **枚举验证**
```go
type Product struct {
    Category string `validate:"oneof=electronics clothing books home"`
    Status   string `validate:"oneof=active inactive pending"`
}
```

## 🔧 **自定义验证器**

为业务特定规则创建验证器：

```go
func validateSKU(fl validator.FieldLevel) bool {
    sku := fl.Field().String()
    // 自定义SKU格式：PROD-12345
    matched, _ := regexp.MatchString(`^PROD-\d{5}$`, sku)
    return matched
}

// 注册自定义验证器
validate := validator.New()
validate.RegisterValidation("sku", validateSKU)
```

### **复杂自定义验证器**
```go
func validateBusinessHours(fl validator.FieldLevel) bool {
    hour := fl.Field().Int()
    // 营业时间：上午9点至下午5点
    return hour >= 9 && hour <= 17
}

func validatePasswordStrength(fl validator.FieldLevel) bool {
    password := fl.Field().String()
    
    // 检查长度
    if len(password) < 8 {
        return false
    }
    
    // 检查大写字母、小写字母、数字、特殊字符
    hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
    hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`\d`).MatchString(password)
    hasSpecial := regexp.MustCompile(`[!@#$%^&*]`).MatchString(password)
    
    return hasUpper && hasLower && hasDigit && hasSpecial
}
```

## 🚨 **错误处理模式**

### **结构化错误响应**
```go
type ValidationError struct {
    Field   string      `json:"field"`
    Tag     string      `json:"tag"`
    Value   interface{} `json:"value"`
    Message string      `json:"message"`
}

type ErrorResponse struct {
    Success bool              `json:"success"`
    Error   string            `json:"error"`
    Details []ValidationError `json:"details,omitempty"`
}
```

### **转换验证错误**
```go
func formatValidationErrors(err error) []ValidationError {
    var errors []ValidationError
    
    if validationErrors, ok := err.(validator.ValidationErrors); ok {
        for _, e := range validationErrors {
            errors = append(errors, ValidationError{
                Field:   e.Field(),
                Tag:     e.Tag(),
                Value:   e.Value(),
                Message: getErrorMessage(e),
            })
        }
    }
    
    return errors
}

func getErrorMessage(e validator.FieldError) string {
    switch e.Tag() {
    case "required":
        return e.Field() + " 是必需的"
    case "email":
        return e.Field() + " 必须是有效的邮箱地址"
    case "min":
        return fmt.Sprintf("%s 至少需要 %s 个字符", e.Field(), e.Param())
    case "max":
        return fmt.Sprintf("%s 不能超过 %s 个字符", e.Field(), e.Param())
    default:
        return e.Field() + " 无效"
    }
}
```

## 🔍 **高级验证技术**

### **跨字段验证**
```go
type User struct {
    Password        string `validate:"required,min=8"`
    ConfirmPassword string `validate:"required,eqfield=Password"`
}

type DateRange struct {
    StartDate time.Time `validate:"required"`
    EndDate   time.Time `validate:"required,gtfield=StartDate"`
}
```

### **条件性验证**
```go
type Product struct {
    Type        string  `validate:"required,oneof=physical digital"`
    Weight      float64 `validate:"required_if=Type physical"`
    FileSize    int64   `validate:"required_if=Type digital"`
    ShippingCost float64 `validate:"excluded_if=Type digital"`
}
```

### **切片验证**
```go
type Order struct {
    Items []Item `validate:"required,dive,required"`
    Tags  []string `validate:"dive,min=2,max=20"`
}

type Item struct {
    Name     string  `validate:"required"`
    Price    float64 `validate:"gt=0"`
    Quantity int     `validate:"gte=1"`
}
```

## 📊 **过滤与搜索模式**

### **查询参数过滤**
```go
func applyFilters(products []Product, c *fiber.Ctx) []Product {
    var filtered []Product
    
    // 获取过滤参数
    category := c.Query("category")
    minPrice := c.Query("min_price")
    maxPrice := c.Query("max_price")
    inStock := c.Query("in_stock")
    search := c.Query("search")
    
    for _, product := range products {
        // 应用过滤条件
        if category != "" && product.Category != category {
            continue
        }
        
        if minPrice != "" {
            if min, err := strconv.ParseFloat(minPrice, 64); err == nil {
                if product.Price < min {
                    continue
                }
            }
        }
        
        if search != "" {
            searchLower := strings.ToLower(search)
            nameMatch := strings.Contains(strings.ToLower(product.Name), searchLower)
            descMatch := strings.Contains(strings.ToLower(product.Description), searchLower)
            if !nameMatch && !descMatch {
                continue
            }
        }
        
        filtered = append(filtered, product)
    }
    
    return filtered
}
```

### **分页支持**
```go
func paginateResults(items []Product, c *fiber.Ctx) ([]Product, map[string]interface{}) {
    page, _ := strconv.Atoi(c.Query("page", "1"))
    limit, _ := strconv.Atoi(c.Query("limit", "10"))
    
    if page < 1 {
        page = 1
    }
    if limit < 1 || limit > 100 {
        limit = 10
    }
    
    offset := (page - 1) * limit
    end := offset + limit
    
    if offset >= len(items) {
        return []Product{}, map[string]interface{}{
            "page":       page,
            "limit":      limit,
            "total":      len(items),
            "total_pages": (len(items) + limit - 1) / limit,
        }
    }
    
    if end > len(items) {
        end = len(items)
    }
    
    return items[offset:end], map[string]interface{}{
        "page":        page,
        "limit":       limit,
        "total":       len(items),
        "total_pages": (len(items) + limit - 1) / limit,
    }
}
```

## 🔒 **安全注意事项**

### **输入清理**
```go
import "html"

func sanitizeInput(input string) string {
    // 移除潜在危险字符
    input = html.EscapeString(input)
    input = strings.TrimSpace(input)
    return input
}
```

### **请求速率验证**
```go
func validateRequestRate(c *fiber.Ctx) error {
    // 限制验证请求以防止滥用
    // 实现取决于你的速率限制策略
    return nil
}
```

## 🧪 **测试验证**

### **单元测试验证器**
```go
func TestProductValidation(t *testing.T) {
    validate := validator.New()
    
    tests := []struct {
        name    string
        product Product
        wantErr bool
    }{
        {
            name: "有效产品",
            product: Product{
                Name:        "测试产品",
                Description: "一个测试产品描述",
                Price:       99.99,
                Category:    "electronics",
                SKU:         "PROD-12345",
            },
            wantErr: false,
        },
        {
            name: "无效价格",
            product: Product{
                Name:        "测试产品",
                Description: "一个测试产品描述",
                Price:       -10.00,
                Category:    "electronics",
                SKU:         "PROD-12345",
            },
            wantErr: true,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := validate.Struct(tt.product)
            hasErr := err != nil
            assert.Equal(t, tt.wantErr, hasErr)
        })
    }
}
```

## 🎯 **最佳实践**

1. **尽早验证**：在输入进入应用时立即检查
2. **清晰的消息**：提供具体且可操作的错误信息
3. **统一格式**：使用标准的错误响应格式
4. **安全优先**：清理输入并根据业务规则进行验证
5. **性能优化**：缓存验证器并避免昂贵的操作
6. **文档化**：在API文档中记录验证规则
7. **测试覆盖**：测试有效和无效输入场景

## 📚 **下一步**

掌握验证与错误处理后：
1. **认证与授权** - 保护你的API
2. **数据库集成** - 持久化已验证的数据
3. **API文档** - 记录验证规则
4. **高级模式** - 异步验证、自定义中间件