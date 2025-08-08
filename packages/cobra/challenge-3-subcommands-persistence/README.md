# 挑战 3：子命令与数据持久化

使用 Cobra 构建一个 **库存管理 CLI**，展示高级子命令组织结构和 JSON 数据持久化功能。

## 挑战要求

创建一个名为 `inventory` 的 CLI 应用程序，用于管理产品库存，具备以下功能：

1. **产品管理** - 添加、列出、更新、删除产品  
2. **分类管理** - 按分类组织产品  
3. **JSON 持久化** - 从 JSON 文件保存/加载数据  
4. **搜索与过滤** - 根据多种条件查找产品  
5. **嵌套子命令** - 组织良好的命令层级结构

## 预期 CLI 结构

```
inventory                          # 根命令
inventory product add              # 添加新产品
inventory product list             # 列出所有产品
inventory product get <id>         # 通过 ID 获取产品
inventory product update <id>      # 更新产品
inventory product delete <id>      # 删除产品
inventory category add             # 添加新分类
inventory category list            # 列出所有分类
inventory search --name <name>     # 按名称搜索产品
inventory search --category <cat>  # 按分类搜索
inventory stats                    # 显示库存统计信息
```

## 示例输出

**添加产品（`inventory product add`）：**
```
$ inventory product add --name "笔记本电脑" --price 999.99 --category "电子产品" --stock 10
✅ 产品添加成功！
ID: 1, 名称: 笔记本电脑, 价格: $999.99, 分类: 电子产品, 库存: 10
```

**列出产品（`inventory product list`）：**
```
$ inventory product list
📦 库存产品：
ID  | 名称          | 价格     | 分类         | 库存
----|---------------|----------|--------------|-------
1   | 笔记本电脑    | $999.99  | 电子产品     | 10
2   | 咖啡杯        | $12.99   | 厨房用品     | 25
3   | 笔记本        | $5.49    | 文具         | 100
```

**搜索产品（`inventory search --category "电子产品"`）：**
```
$ inventory search --category "电子产品"
🔍 在分类 "电子产品" 中找到 1 个产品：
ID  | 名称          | 价格     | 库存
----|---------------|----------|-------
1   | 笔记本电脑    | $999.99  | 10
```

**统计信息（`inventory stats`）：**
```
$ inventory stats
📊 库存统计信息：
- 总产品数量：3
- 总分类数量：3
- 总价值：$1,018.47
- 低库存商品（< 5）：0
- 缺货商品：0
```

## 数据模型

```go
type Product struct {
    ID       int     `json:"id"`
    Name     string  `json:"name"`
    Price    float64 `json:"price"`
    Category string  `json:"category"`
    Stock    int     `json:"stock"`
}

type Category struct {
    Name        string `json:"name"`
    Description string `json:"description"`
}

type Inventory struct {
    Products   []Product  `json:"products"`
    Categories []Category `json:"categories"`
    NextID     int        `json:"next_id"`
}
```

## 实现要求

### 产品子命令
- `product add` - 添加新产品，支持参数：`--name`、`--price`、`--category`、`--stock`
- `product list` - 以表格格式显示所有产品
- `product get <id>` - 显示指定产品的详细信息
- `product update <id>` - 使用与添加相同的参数更新产品
- `product delete <id>` - 从库存中移除产品

### 分类子命令
- `category add` - 添加新分类，支持参数：`--name`、`--description`
- `category list` - 显示所有分类

### 搜索命令
- `search` - 搜索产品，支持参数：`--name`、`--category`、`--min-price`、`--max-price`

### 数据持久化
- 将数据存储在 `inventory.json` 文件中
- 若文件不存在则自动创建
- 启动时加载数据，修改后保存
- 优雅处理文件读写错误

### 错误处理
- 验证必需参数
- 检查重复的产品/分类名称
- 处理无效 ID
- 提供清晰的错误提示信息

## 测试要求

你的解决方案必须通过以下测试：
- 所有子命令正确执行
- 数据持久化功能正常（从 JSON 保存/加载）
- 产品增删改查操作正常
- 分类管理功能正常
- 不同过滤条件下的搜索功能正常
- 统计计算准确无误
- 对无效输入的错误处理正确
- 命令结构符合预期层级关系