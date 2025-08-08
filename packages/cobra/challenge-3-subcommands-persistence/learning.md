# 学习：高级 Cobra 子命令与数据持久化

## 🌟 **高级 Cobra 概念**

本挑战介绍了构建生产级应用程序所必需的复杂 CLI 模式。你将学习如何创建复杂的命令层级结构，并实现数据持久化策略。

### **为何这些模式至关重要**
- **可扩展性**：嵌套命令允许功能模块化组织
- **用户体验**：逻辑命令分组提升命令的可发现性
- **数据管理**：持久化支持有状态的 CLI 应用程序
- **实际应用**：大多数生产环境 CLI 都采用这些模式

## 🏗️ **命令层级与组织**

### **1. 嵌套命令结构**

现代 CLI 将功能按逻辑分组：

```
inventory                    # 根命令
├── product                  # 产品操作的父命令
│   ├── add                 # 产品管理子命令
│   ├── list
│   ├── get <id>
│   ├── update <id>
│   └── delete <id>
├── category                 # 分类操作的父命令
│   ├── add
│   └── list
├── search                   # 独立的搜索命令
└── stats                    # 独立的统计命令
```

### **2. 命令分组策略**

**按实体类型分组：**
```go
// 将所有与产品相关的命令归入 'product'
var productCmd = &cobra.Command{
    Use:   "product",
    Short: "管理库存中的产品",
}

// 将所有与分类相关的命令归入 'category'
var categoryCmd = &cobra.Command{
    Use:   "category", 
    Short: "管理分类",
}
```

**按操作类型分组：**
```go
// 另一种方式：按 CRUD 操作分组
var createCmd = &cobra.Command{Use: "create", Short: "创建资源"}
var listCmd = &cobra.Command{Use: "list", Short: "列出资源"}
var updateCmd = &cobra.Command{Use: "update", Short: "更新资源"}
var deleteCmd = &cobra.Command{Use: "delete", Short: "删除资源"}
```

### **3. 命令注册模式**

**层级注册：**
```go
func init() {
    // 自下而上构建命令树
    productCmd.AddCommand(productAddCmd)
    productCmd.AddCommand(productListCmd)
    productCmd.AddCommand(productGetCmd)
    productCmd.AddCommand(productUpdateCmd)
    productCmd.AddCommand(productDeleteCmd)
    
    categoryCmd.AddCommand(categoryAddCmd)
    categoryCmd.AddCommand(categoryListCmd)
    
    // 将父命令注册到根命令
    rootCmd.AddCommand(productCmd)
    rootCmd.AddCommand(categoryCmd)
    rootCmd.AddCommand(searchCmd)
    rootCmd.AddCommand(statsCmd)
}
```

## 💾 **数据持久化策略**

### **1. 基于文件的持久化**

**JSON 存储模式：**
```go
type Inventory struct {
    Products   []Product  `json:"products"`
    Categories []Category `json:"categories"`
    NextID     int        `json:"next_id"`
}

const inventoryFile = "inventory.json"

func LoadInventory() error {
    if _, err := os.Stat(inventoryFile); os.IsNotExist(err) {
        return createDefaultInventory()
    }
    
    data, err := ioutil.ReadFile(inventoryFile)
    if err != nil {
        return fmt.Errorf("读取库存文件失败: %w", err)
    }
    
    if err := json.Unmarshal(data, &inventory); err != nil {
        return fmt.Errorf("解析库存数据失败: %w", err)
    }
    
    return nil
}

func SaveInventory() error {
    data, err := json.MarshalIndent(inventory, "", "  ")
    if err != nil {
        return fmt.Errorf("序列化库存失败: %w", err)
    }
    
    if err := ioutil.WriteFile(inventoryFile, data, 0644); err != nil {
        return fmt.Errorf("写入库存文件失败: %w", err)
    }
    
    return nil
}
```

### **2. 原子操作**

**安全更新模式：**
```go
func UpdateProduct(id int, updates map[string]interface{}) error {
    // 查找产品
    product, index := FindProductByID(id)
    if product == nil {
        return fmt.Errorf("产品 %d 不存在", id)
    }
    
    // 创建备份用于回滚
    backup := *product
    
    // 应用更新
    for field, value := range updates {
        switch field {
        case "name":
            if name, ok := value.(string); ok {
                product.Name = name
            }
        case "price":
            if price, ok := value.(float64); ok {
                product.Price = price
            }
        // ... 其他字段
        }
    }
    
    // 验证更新后的数据
    if err := ValidateProduct(product); err != nil {
        // 验证失败时回滚
        inventory.Products[index] = backup
        return fmt.Errorf("验证失败: %w", err)
    }
    
    // 持久化更改
    if err := SaveInventory(); err != nil {
        // 保存失败时回滚
        inventory.Products[index] = backup
        return fmt.Errorf("保存失败: %w", err)
    }
    
    return nil
}
```

### **3. 数据验证**

**输入验证流水线：**
```go
func ValidateProduct(product *Product) error {
    var errors []string
    
    if product.Name == "" {
        errors = append(errors, "名称不能为空")
    }
    
    if product.Price <= 0 {
        errors = append(errors, "价格必须为正数")
    }
    
    if product.Stock < 0 {
        errors = append(errors, "库存不能为负数")
    }
    
    if len(errors) > 0 {
        return fmt.Errorf("验证错误: %s", strings.Join(errors, ", "))
    }
    
    return nil
}
```

## 🚩 **高级标志模式**

### **1. 命令特定标志**

**产品创建标志：**
```go
func init() {
    productAddCmd.Flags().StringP("name", "n", "", "产品名称（必填）")
    productAddCmd.Flags().Float64P("price", "p", 0, "产品价格（必填）")
    productAddCmd.Flags().StringP("category", "c", "", "产品分类（必填）")
    productAddCmd.Flags().IntP("stock", "s", 0, "库存数量（必填）")
    
    // 标记必填标志
    productAddCmd.MarkFlagRequired("name")
    productAddCmd.MarkFlagRequired("price")
    productAddCmd.MarkFlagRequired("category")
    productAddCmd.MarkFlagRequired("stock")
}
```

**带可选过滤器的搜索标志：**
```go
func init() {
    searchCmd.Flags().StringP("name", "n", "", "按产品名称筛选")
    searchCmd.Flags().StringP("category", "c", "", "按分类筛选")
    searchCmd.Flags().Float64("min-price", 0, "最低价格筛选")
    searchCmd.Flags().Float64("max-price", 0, "最高价格筛选")
    searchCmd.Flags().BoolP("in-stock", "i", false, "仅显示有库存的商品")
}
```

### **2. 标志验证**

**自定义验证逻辑：**
```go
func validateFlags(cmd *cobra.Command) error {
    minPrice, _ := cmd.Flags().GetFloat64("min-price")
    maxPrice, _ := cmd.Flags().GetFloat64("max-price")
    
    if minPrice > 0 && maxPrice > 0 && minPrice > maxPrice {
        return fmt.Errorf("最小价格不能大于最大价格")
    }
    
    return nil
}
```

## 🔍 **搜索与过滤实现**

### **1. 多条件搜索**

```go
type SearchCriteria struct {
    Name      string
    Category  string
    MinPrice  float64
    MaxPrice  float64
    InStock   bool
}

func SearchProducts(criteria SearchCriteria) []Product {
    var results []Product
    
    for _, product := range inventory.Products {
        if matchesCriteria(product, criteria) {
            results = append(results, product)
        }
    }
    
    return results
}

func matchesCriteria(product Product, criteria SearchCriteria) bool {
    // 名称筛选
    if criteria.Name != "" {
        if !strings.Contains(strings.ToLower(product.Name), strings.ToLower(criteria.Name)) {
            return false
        }
    }
    
    // 分类筛选
    if criteria.Category != "" {
        if strings.ToLower(product.Category) != strings.ToLower(criteria.Category) {
            return false
        }
    }
    
    // 价格范围筛选
    if criteria.MinPrice > 0 && product.Price < criteria.MinPrice {
        return false
    }
    if criteria.MaxPrice > 0 && product.Price > criteria.MaxPrice {
        return false
    }
    
    // 库存筛选
    if criteria.InStock && product.Stock <= 0 {
        return false
    }
    
    return true
}
```

### **2. 结果格式化**

**灵活的输出格式：**
```go
func DisplaySearchResults(products []Product, criteria SearchCriteria) {
    fmt.Printf("🔍 找到 %d 个商品", len(products))
    
    // 显示当前激活的筛选条件
    filters := []string{}
    if criteria.Name != "" {
        filters = append(filters, fmt.Sprintf("名称包含 '%s'", criteria.Name))
    }
    if criteria.Category != "" {
        filters = append(filters, fmt.Sprintf("分类为 '%s'", criteria.Category))
    }
    if criteria.MinPrice > 0 || criteria.MaxPrice > 0 {
        if criteria.MinPrice > 0 && criteria.MaxPrice > 0 {
            filters = append(filters, fmt.Sprintf("价格在 $%.2f 到 $%.2f 之间", criteria.MinPrice, criteria.MaxPrice))
        } else if criteria.MinPrice > 0 {
            filters = append(filters, fmt.Sprintf("价格 >= $%.2f", criteria.MinPrice))
        } else {
            filters = append(filters, fmt.Sprintf("价格 <= $%.2f", criteria.MaxPrice))
        }
    }
    
    if len(filters) > 0 {
        fmt.Printf(" 匹配: %s", strings.Join(filters, ", "))
    }
    fmt.Println()
    
    if len(products) == 0 {
        fmt.Println("未找到符合筛选条件的商品。")
        return
    }
    
    displayProductsTable(products)
}
```

## 📊 **统计与分析**

### **1. 综合指标**

```go
type InventoryStats struct {
    TotalProducts    int
    TotalCategories  int
    TotalValue       float64
    AveragePrice     float64
    LowStockCount    int
    OutOfStockCount  int
    TopCategory      string
    CategoryStats    map[string]CategoryStat
}

type CategoryStat struct {
    ProductCount int
    TotalValue   float64
    AveragePrice float64
}

func CalculateStats() InventoryStats {
    stats := InventoryStats{
        CategoryStats: make(map[string]CategoryStat),
    }
    
    stats.TotalProducts = len(inventory.Products)
    stats.TotalCategories = len(inventory.Categories)
    
    categoryProductCount := make(map[string]int)
    categoryValues := make(map[string]float64)
    
    for _, product := range inventory.Products {
        // 总价值计算
        productValue := product.Price * float64(product.Stock)
        stats.TotalValue += productValue
        
        // 库存分析
        if product.Stock == 0 {
            stats.OutOfStockCount++
        } else if product.Stock < 5 {
            stats.LowStockCount++
        }
        
        // 分类分析
        categoryProductCount[product.Category]++
        categoryValues[product.Category] += productValue
    }
    
    // 计算平均值
    if stats.TotalProducts > 0 {
        stats.AveragePrice = stats.TotalValue / float64(stats.TotalProducts)
    }
    
    // 找出最畅销分类
    maxProducts := 0
    for category, count := range categoryProductCount {
        if count > maxProducts {
            maxProducts = count
            stats.TopCategory = category
        }
        
        stats.CategoryStats[category] = CategoryStat{
            ProductCount: count,
            TotalValue:   categoryValues[category],
            AveragePrice: categoryValues[category] / float64(count),
        }
    }
    
    return stats
}
```

## 🎯 **CLI 数据管理的最佳实践**

### **1. 错误恢复模式**

- **优雅降级**：当非关键数据损坏时，仍能继续运行并发出警告
- **备份策略**：在破坏性操作前保留备份文件
- **验证关卡**：在重大操作前验证数据完整性

### **2. 性能考虑**

- **延迟加载**：仅在需要时才加载数据
- **索引**：为频繁查询创建内存索引
- **缓存**：缓存计算出的统计数据和搜索结果

### **3. 用户体验**

- **进度指示**：对长时间运行的操作显示进度
- **确认提示**：对破坏性操作要求用户确认
- **清晰提示**：提供明确且可操作的错误信息

本挑战通过引入可随复杂度和使用量增长的企业级模式，弥合了简单 CLI 工具与生产级应用之间的差距。