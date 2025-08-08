# 学习材料：带验证与错误处理的 JSON API

## 🎯 **你将学到的内容**

本挑战将教你高级验证模式和错误处理技术，这些技术对于在生产环境中构建健壮的 API 至关重要。

## 📚 **核心概念**

### **1. 输入验证层级**

现代 API 使用多层验证：

```go
// 第一层：基本 JSON 绑定验证（内置）
if err := c.ShouldBindJSON(&product); err != nil {
    // 处理基本格式错误
}

// 第二层：自定义业务逻辑验证
errors := validateProduct(&product)

// 第三层：跨字段和上下文验证
errors = append(errors, validateBusinessRules(&product)...)
```

### **2. 自定义验证函数**

创建可重用的验证函数以处理复杂的业务规则：

```go
// 正则表达式验证
func isValidSKU(sku string) bool {
    pattern := `^[A-Z]{3}-\d{3}-[A-Z]{3}$`
    matched, _ := regexp.MatchString(pattern, sku)
    return matched
}

// 列表验证
func isValidCurrency(currency string) bool {
    validCurrencies := []string{"USD", "EUR", "GBP", "JPY"}
    for _, valid := range validCurrencies {
        if currency == valid {
            return true
        }
    }
    return false
}

// 跨字段验证
func validateInventoryRules(inventory Inventory) []ValidationError {
    var errors []ValidationError
    
    if inventory.Reserved > inventory.Quantity {
        errors = append(errors, ValidationError{
            Field:   "inventory.reserved",
            Message: "预留数量不能超过库存数量",
        })
    }
    
    return errors
}
```

### **3. 错误响应标准化**

一致的错误响应能提升 API 的可用性：

```go
type ValidationError struct {
    Field   string      `json:"field"`
    Value   interface{} `json:"value"`
    Tag     string      `json:"tag"`
    Message string      `json:"message"`
    Param   string      `json:"param,omitempty"`
}

type APIResponse struct {
    Success   bool              `json:"success"`
    Data      interface{}       `json:"data,omitempty"`
    Message   string            `json:"message,omitempty"`
    Errors    []ValidationError `json:"errors,omitempty"`
    ErrorCode string            `json:"error_code,omitempty"`
    RequestID string            `json:"request_id,omitempty"`
}
```

## 🔧 **输入净化模式**

在验证前始终对输入进行净化：

```go
func sanitizeProduct(product *Product) {
    // 去除首尾空白字符
    product.Name = strings.TrimSpace(product.Name)
    product.SKU = strings.TrimSpace(product.SKU)
    
    // 统一大小写
    product.Currency = strings.ToUpper(product.Currency)
    product.Category.Slug = strings.ToLower(product.Category.Slug)
    
    // 计算衍生字段
    product.Inventory.Available = product.Inventory.Quantity - product.Inventory.Reserved
    
    // 设置系统字段
    if product.ID == 0 {
        product.CreatedAt = time.Now()
    }
    product.UpdatedAt = time.Now()
}
```

## 🏗️ **正则表达式模式**

常见的验证模式：

```go
// SKU 格式：ABC-123-XYZ
var skuPattern = `^[A-Z]{3}-\d{3}-[A-Z]{3}$`

// URL 友好别名：小写字母加连字符
var slugPattern = `^[a-z0-9]+(?:-[a-z0-9]+)*$`

// 仓库代码：WH001、WH002 等
var warehousePattern = `^WH\d{3}$`

// 邮箱验证（基础版）
var emailPattern = `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

// 电话号码（美国格式）
var phonePattern = `^\(\d{3}\) \d{3}-\d{4}$`
```

## 📊 **批量操作最佳实践**

对批量操作提供详细反馈：

```go
type BulkResult struct {
    Index   int               `json:"index"`
    Success bool              `json:"success"`
    Product *Product          `json:"product,omitempty"`
    Errors  []ValidationError `json:"errors,omitempty"`
}

func processBulkData(items []Product) []BulkResult {
    var results []BulkResult
    
    for i, item := range items {
        errors := validateProduct(&item)
        
        if len(errors) > 0 {
            results = append(results, BulkResult{
                Index:   i,
                Success: false,
                Errors:  errors,
            })
        } else {
            // 处理成功项
            sanitizeProduct(&item)
            // 保存到数据库/存储
            
            results = append(results, BulkResult{
                Index:   i,
                Success: true,
                Product: &item,
            })
        }
    }
    
    return results
}
```

## 🌐 **本地化与错误消息**

支持多种语言的错误消息：

```go
var ErrorMessages = map[string]map[string]string{
    "en": {
        "required":      "此字段为必填项",
        "min":           "值必须至少为 %s",
        "max":           "值最多为 %s",
        "sku_format":    "SKU 必须符合 ABC-123-XYZ 格式",
        "invalid_currency": "必须是有效的货币代码",
    },
    "es": {
        "required":      "Este campo es obligatorio",
        "min":           "El valor debe ser al menos %s",
        "sku_format":    "SKU debe seguir el formato ABC-123-XYZ",
    },
}

func getLocalizedMessage(lang, key string, params ...string) string {
    messages, exists := ErrorMessages[lang]
    if !exists {
        messages = ErrorMessages["en"] // 回退到英文
    }
    
    message, exists := messages[key]
    if !exists {
        return "验证失败"
    }
    
    // 处理参数替换
    for i, param := range params {
        placeholder := fmt.Sprintf("%%s")
        if i == 0 {
            message = strings.Replace(message, placeholder, param, 1)
        }
    }
    
    return message
}
```

## 🔐 **安全注意事项**

### **1. 输入净化**
```go
// 移除危险字符
func sanitizeString(input string) string {
    // 移除 HTML 标签
    input = regexp.MustCompile(`<[^>]*>`).ReplaceAllString(input, "")
    
    // 移除 SQL 注入尝试
    dangerous := []string{"'", "\"", ";", "--", "/*", "*/"}
    for _, char := range dangerous {
        input = strings.ReplaceAll(input, char, "")
    }
    
    return strings.TrimSpace(input)
}
```

### **2. 批量操作的速率限制**
```go
const maxBulkSize = 100

func createProductsBulk(c *gin.Context) {
    var products []Product
    
    if err := c.ShouldBindJSON(&products); err != nil {
        c.JSON(400, APIResponse{
            Success: false,
            Message: "无效的 JSON",
        })
        return
    }
    
    if len(products) > maxBulkSize {
        c.JSON(400, APIResponse{
            Success: false,
            Message: fmt.Sprintf("批量大小不能超过 %d 项", maxBulkSize),
        })
        return
    }
    
    // 处理批量操作...
}
```

## 🧪 **测试验证逻辑**

彻底测试每个验证函数：

```go
func TestSKUValidation(t *testing.T) {
    tests := []struct {
        name     string
        sku      string
        expected bool
    }{
        {"有效 SKU", "ABC-123-XYZ", true},
        {"无效 - 小写", "abc-123-xyz", false},
        {"无效 - 格式错误", "ABC123XYZ", false},
        {"空字符串", "", false},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := isValidSKU(tt.sku)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

## 💡 **性能优化**

### **1. 预编译正则表达式**
```go
var (
    skuRegex       = regexp.MustCompile(`^[A-Z]{3}-\d{3}-[A-Z]{3}$`)
    slugRegex      = regexp.MustCompile(`^[a-z0-9]+(?:-[a-z0-9]+)*$`)
    warehouseRegex = regexp.MustCompile(`^WH\d{3}$`)
)

func isValidSKU(sku string) bool {
    return skuRegex.MatchString(sku)
}
```

### **2. 使用映射进行查找**
```go
var validCurrencies = map[string]bool{
    "USD": true,
    "EUR": true,
    "GBP": true,
    "JPY": true,
}

func isValidCurrency(currency string) bool {
    return validCurrencies[currency]
}
```

## 🏭 **实际应用场景**

这些模式被用于：

- **电商平台** - 商品目录验证
- **金融系统** - 交易数据验证
- **医疗健康 API** - 患者数据验证
- **SaaS 平台** - 多租户数据验证
- **数据导入系统** - 批量数据处理

## 📈 **高级主题**

### **1. 条件验证**
```go
func validateProductByCategory(product *Product) []ValidationError {
    var errors []ValidationError
    
    switch product.Category.Name {
    case "Electronics":
        // 电子产品需要保修信息
        if len(product.Images) == 0 {
            errors = append(errors, ValidationError{
                Field:   "images",
                Message: "电子产品必须包含产品图片",
            })
        }
    case "Clothing":
        // 服装需要尺寸信息
        if _, hasSize := product.Attributes["size"]; !hasSize {
            errors = append(errors, ValidationError{
                Field:   "attributes.size",
                Message: "服装必须指定尺寸",
            })
        }
    }
    
    return errors
}
```

### **2. 异步验证**
```go
func validateSKUUniqueness(sku string) <-chan ValidationResult {
    result := make(chan ValidationResult, 1)
    
    go func() {
        defer close(result)
        
        // 检查数据库中是否存在该 SKU
        exists := checkSKUInDatabase(sku)
        
        result <- ValidationResult{
            Valid: !exists,
            Error: func() string {
                if exists {
                    return "SKU 已存在"
                }
                return ""
            }(),
        }
    }()
    
    return result
}
```

掌握这些概念将帮助你构建具备全面验证和错误处理能力的健壮、可投入生产的 API。