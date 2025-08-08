# 挑战 3：带验证与错误处理的 JSON API

构建一个**产品目录 API**，包含全面的输入验证、自定义验证器以及健壮的错误处理机制。

## 挑战要求

实现一个 JSON API，包含以下端点：

- `POST /products` - 创建新产品并进行验证
- `PUT /products/:id` - 更新产品并进行验证
- `POST /products/bulk` - 在一次请求中创建多个产品
- `GET /products` - 获取所有产品，支持可选过滤
- `GET /products/:id` - 根据 ID 获取产品

## 数据结构

```go
type Product struct {
    ID          int     `json:"id"`
    Name        string  `json:"name" binding:"required,min=2,max=100"`
    Description string  `json:"description" binding:"required,min=10,max=500"`
    Price       float64 `json:"price" binding:"required,gt=0"`
    Category    string  `json:"category" binding:"required,oneof=electronics clothing books home"`
    SKU         string  `json:"sku" binding:"required,sku"`
    InStock     bool    `json:"in_stock"`
    Tags        []string `json:"tags" binding:"dive,min=2,max=20"`
}
```

## 验证要求

### 内置验证器
- **required**：字段必须存在
- **min/max**：字符串长度或数值范围验证
- **gt**：大于（价格 > 0）
- **oneof**：值必须是指定选项之一

### 自定义验证器
- **sku**：SKU 格式验证（例如："PROD-12345"）
- **dive**：验证切片中的每个元素

## 错误响应格式

```json
{
    "success": false,
    "error": "验证失败",
    "details": [
        {
            "field": "name",
            "message": "名称为必填项，且长度需在 2-100 字符之间"
        },
        {
            "field": "price", 
            "message": "价格必须大于 0"
        }
    ]
}
```

## 测试要求

你的解决方案必须通过以下测试：
- 字段存在性验证（必填字段）
- 字符串长度验证（最小/最大长度）
- 数值验证（价格 > 0）
- 枚举值验证（类别取值）
- 自定义 SKU 格式验证
- 数组元素验证（标签）
- 批量操作验证（支持部分失败）
- 正确的错误响应格式
- Content-Type 验证（必须为 application/json）