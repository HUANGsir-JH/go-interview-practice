# 挑战3提示：带验证和错误处理的JSON API

## 提示1：实现SKU格式验证

使用正则表达式来验证SKU格式 ABC-123-XYZ：

```go
func isValidSKU(sku string) bool {
    matched, _ := regexp.MatchString(`^[A-Z]{3}-\d{3}-[A-Z]{3}$`, sku)
    return matched
}
```

## 提示2：货币和分类验证

使用切片查找预定义的有效值：

```go
func isValidCurrency(currency string) bool {
    for _, valid := range validCurrencies {
        if currency == valid {
            return true
        }
    }
    return false
}

func isValidCategory(categoryName string) bool {
    for _, category := range categories {
        if category.Name == categoryName {
            return true
        }
    }
    return false
}
```

## 提示3：构建全面的产品验证

创建一个检查所有业务规则的验证函数：

```go
func validateProduct(product *Product) []ValidationError {
    var errors []ValidationError
    
    // SKU验证
    if !isValidSKU(product.SKU) {
        errors = append(errors, ValidationError{
            Field:   "sku",
            Value:   product.SKU,
            Tag:     "sku_format",
            Message: "SKU必须符合ABC-123-XYZ格式",
        })
    }
    
    // 货币验证
    if !isValidCurrency(product.Currency) {
        errors = append(errors, ValidationError{
            Field:   "currency",
            Value:   product.Currency,
            Tag:     "iso4217",
            Message: "必须是有效的ISO 4217货币代码",
        })
    }
    
    // 跨字段验证
    if product.Inventory.Reserved > product.Inventory.Quantity {
        errors = append(errors, ValidationError{
            Field:   "inventory.reserved",
            Value:   product.Inventory.Reserved,
            Tag:     "max",
            Message: "预留库存不能超过总数量",
        })
    }
    
    return errors
}
```

## 提示4：输入数据净化实现

在验证前清理和标准化输入数据：

```go
func sanitizeProduct(product *Product) {
    // 去除空白字符
    product.SKU = strings.TrimSpace(product.SKU)
    product.Name = strings.TrimSpace(product.Name)
    product.Description = strings.TrimSpace(product.Description)
    
    // 标准化大小写
    product.Currency = strings.ToUpper(product.Currency)
    product.Category.Slug = strings.ToLower(product.Category.Slug)
    
    // 计算计算字段
    product.Inventory.Available = product.Inventory.Quantity - product.Inventory.Reserved
    
    // 设置时间戳
    now := time.Now()
    if product.ID == 0 {
        product.CreatedAt = now
    }
    product.UpdatedAt = now
}
```

## 提示5：Slug格式验证

验证适合URL的slug格式：

```go
func isValidSlug(slug string) bool {
    // Slug应为小写，仅包含字母数字和连字符
    matched, _ := regexp.MatchString(`^[a-z0-9]+(?:-[a-z0-9]+)*$`, slug)
    return matched
}
```

## 提示6：仓库代码验证

检查仓库代码是否在预定义列表中：

```go
func isValidWarehouseCode(code string) bool {
    for _, valid := range validWarehouses {
        if code == valid {
            return true
        }
    }
    return false
}
```

## 提示7：处理Gin验证错误

将Gin的验证错误转换为自定义格式：

```go
func createProduct(c *gin.Context) {
    var product Product
    
    if err := c.ShouldBindJSON(&product); err != nil {
        // 处理Gin验证错误
        var ginErrors []ValidationError
        
        // 将Gin验证错误转换为自定义格式
        // 这是基础版本——你可以进一步增强错误提取
        ginErrors = append(ginErrors, ValidationError{
            Field:   "various",
            Message: "基本验证失败",
            Tag:     "binding",
        })
        
        c.JSON(400, APIResponse{
            Success: false,
            Message: "验证失败",
            Errors:  ginErrors,
        })
        return
    }
    
    // 继续进行自定义验证...
}
```

## 提示8：批量操作并返回详细结果

逐个处理每个项目并收集结果：

```go
func createProductsBulk(c *gin.Context) {
    var inputProducts []Product
    
    if err := c.ShouldBindJSON(&inputProducts); err != nil {
        c.JSON(400, APIResponse{
            Success: false,
            Message: "无效的JSON格式",
        })
        return
    }
    
    type BulkResult struct {
        Index   int               `json:"index"`
        Success bool              `json:"success"`
        Product *Product          `json:"product,omitempty"`
        Errors  []ValidationError `json:"errors,omitempty"`
    }
    
    var results []BulkResult
    var successCount int
    
    for i, product := range inputProducts {
        validationErrors := validateProduct(&product)
        if len(validationErrors) > 0 {
            results = append(results, BulkResult{
                Index:   i,
                Success: false,
                Errors:  validationErrors,
            })
        } else {
            sanitizeProduct(&product)
            product.ID = nextProductID
            nextProductID++
            products = append(products, product)
            
            results = append(results, BulkResult{
                Index:   i,
                Success: true,
                Product: &product,
            })
            successCount++
        }
    }
    
    c.JSON(200, APIResponse{
        Success: successCount == len(inputProducts),
        Data: map[string]interface{}{
            "results":    results,
            "total":      len(inputProducts),
            "successful": successCount,
            "failed":     len(inputProducts) - successCount,
        },
        Message: "批量操作已完成",
    })
}
```