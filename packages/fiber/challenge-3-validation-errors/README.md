# 挑战3：带验证与错误处理的JSON API

构建一个**产品目录API**，包含全面的输入验证、自定义验证器和健壮的错误处理。

## 挑战要求

实现一个具有以下端点的JSON API：

- `POST /products` - 创建新产品并进行验证
- `PUT /products/:id` - 更新产品并进行验证
- `POST /products/bulk` - 在一次请求中创建多个产品
- `GET /products` - 获取所有产品，支持可选过滤
- `GET /products/:id` - 根据ID获取产品

## 数据结构

```go
type Product struct {
    ID          int      `json:"id"`
    Name        string   `json:"name" validate:"required,min=2,max=100"`
    Description string   `json:"description" validate:"required,min=10,max=500"`
    Price       float64  `json:"price" validate:"required,gt=0"`
    Category    string   `json:"category" validate:"required,oneof=electronics clothing books home"`
    SKU         string   `json:"sku" validate:"required,sku"`
    InStock     bool     `json:"in_stock"`
    Tags        []string `json:"tags" validate:"dive,min=2,max=20"`
}
```

## 验证要求

### 内置验证器
- **required**：字段必须存在
- **min/max**：字符串长度或数值范围验证
- **gt**：大于（价格 > 0）
- **oneof**：值必须是指定选项之一

### 自定义验证器
- **sku**：SKU格式验证（例如："PROD-12345"）
- **dive**：验证切片中的每个元素

## 错误响应格式

```json
{
    "success": false,
    "error": "验证失败",
    "details": [
        {
            "field": "name",
            "tag": "required",
            "value": "",
            "message": "名称为必填项"
        },
        {
            "field": "price",
            "tag": "gt",
            "value": -5.0,
            "message": "价格必须大于0"
        }
    ]
}
```

## 测试要求

你的解决方案必须能够处理：
- 字段存在性验证（必填字段）
- 字符串长度验证（min/max）
- 数值范围验证（gt, gte, lt, lte）
- 枚举验证（oneof）
- 自定义SKU格式验证
- 切片元素验证（dive）
- 批量创建时的部分失败情况
- 正确的错误响应格式