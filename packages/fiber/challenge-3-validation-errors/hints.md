# 挑战3提示：带验证和错误处理的JSON API

## 提示1：设置验证器

使用 validator 包进行结构体验证：

```go
import "github.com/go-playground/validator/v10"

var validate *validator.Validate

func init() {
    validate = validator.New()
    validate.RegisterValidation("sku", validateSKU)
}
```

## 提示2：自定义SKU验证器

实现SKU格式验证：

```go
func validateSKU(fl validator.FieldLevel) bool {
    sku := fl.Field().String()
    // 匹配模式：PROD-XXXXX（其中X为数字）
    matched, _ := regexp.MatchString(`^PROD-\d{5}$`, sku)
    return matched
}
```

## 提示3：验证错误处理

将验证错误转换为自定义格式：

```go
func validateProduct(product Product) []ValidationError {
    err := validate.Struct(product)
    if err == nil {
        return nil
    }
    
    var errors []ValidationError
    for _, err := range err.(validator.ValidationErrors) {
        validationErr := formatValidationError(
            err.Field(),
            err.Tag(),
            err.Value(),
        )
        errors = append(errors, validationErr)
    }
    
    return errors
}
```

## 提示4：自定义错误消息

创建用户友好的错误消息：

```go
func formatValidationError(field, tag string, value interface{}) ValidationError {
    var message string
    
    switch tag {
    case "required":
        message = field + " 是必填项"
    case "min":
        message = fmt.Sprintf("%s 至少需要 %s 个字符", field, "X")
    case "max":
        message = fmt.Sprintf("%s 不能超过 %s 个字符", field, "X")
    case "gt":
        message = fmt.Sprintf("%s 必须大于 0", field)
    case "oneof":
        message = fmt.Sprintf("%s 必须是以下之一：electronics, clothing, books, home", field)
    case "sku":
        message = fmt.Sprintf("%s 必须符合 PROD-XXXXX 格式", field)
    default:
        message = fmt.Sprintf("%s 无效", field)
    }
    
    return ValidationError{
        Field:   field,
        Tag:     tag,
        Value:   value,
        Message: message,
    }
}
```

## 提示5：过滤功能实现

添加查询参数过滤功能：

```go
func filterProducts(products []Product, filters map[string]string) []Product {
    var filtered []Product
    
    for _, product := range products {
        include := true
        
        // 按类别过滤
        if category, exists := filters["category"]; exists {
            if product.Category != category {
                include = false
            }
        }
        
        // 按库存状态过滤
        if inStock, exists := filters["in_stock"]; exists {
            if stockBool, _ := strconv.ParseBool(inStock); product.InStock != stockBool {
                include = false
            }
        }
        
        // 按价格范围过滤
        if minPrice, exists := filters["min_price"]; exists {
            if min, _ := strconv.ParseFloat(minPrice, 64); product.Price < min {
                include = false
            }
        }
        
        if include {
            filtered = append(filtered, product)
        }
    }
    
    return filtered
}
```

## 提示6：批量操作

处理批量创建并允许部分失败：

```go
func bulkCreateHandler(c *fiber.Ctx) error {
    var products []Product
    if err := c.BodyParser(&products); err != nil {
        return c.Status(400).JSON(ErrorResponse{
            Success: false,
            Error:   "无效的JSON格式",
        })
    }
    
    type BulkResult struct {
        Success bool        `json:"success"`
        Product *Product    `json:"product,omitempty"`
        Errors  []ValidationError `json:"errors,omitempty"`
    }
    
    var results []BulkResult
    
    for _, product := range products {
        if errors := validateProduct(product); len(errors) > 0 {
            results = append(results, BulkResult{
                Success: false,
                Errors:  errors,
            })
        } else {
            // 创建商品
            product.ID = nextID
            nextID++
            products = append(products, product)
            
            results = append(results, BulkResult{
                Success: true,
                Product: &product,
            })
        }
    }
    
    return c.JSON(fiber.Map{
        "success": true,
        "results": results,
    })
}
```