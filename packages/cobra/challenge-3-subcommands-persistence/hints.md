# 挑战3提示：子命令与数据持久化

## 提示1：设置根命令

配置库存CLI的根命令：

```go
var rootCmd = &cobra.Command{
    Use:   "inventory",
    Short: "库存管理CLI - 管理您的产品和分类",
    Long:  "一个完整的库存管理系统，支持产品和分类管理、数据持久化以及搜索功能。",
}
```

## 提示2：创建嵌套命令结构

使用 `AddCommand()` 创建分层命令：

```go
func init() {
    // 添加产品子命令
    productCmd.AddCommand(productAddCmd)
    productCmd.AddCommand(productListCmd)
    productCmd.AddCommand(productGetCmd)
    productCmd.AddCommand(productUpdateCmd)
    productCmd.AddCommand(productDeleteCmd)
    
    // 添加分类子命令
    categoryCmd.AddCommand(categoryAddCmd)
    categoryCmd.AddCommand(categoryListCmd)
    
    // 将所有命令添加到根命令
    rootCmd.AddCommand(productCmd)
    rootCmd.AddCommand(categoryCmd)
    rootCmd.AddCommand(searchCmd)
    rootCmd.AddCommand(statsCmd)
}
```

## 提示3：为命令添加标志

添加用户输入的标志：

```go
func init() {
    // 产品添加标志
    productAddCmd.Flags().StringP("name", "n", "", "产品名称（必需）")
    productAddCmd.Flags().Float64P("price", "p", 0, "产品价格（必需）")
    productAddCmd.Flags().StringP("category", "c", "", "产品分类（必需）")
    productAddCmd.Flags().IntP("stock", "s", 0, "库存数量（必需）")
    
    // 标记必需标志
    productAddCmd.MarkFlagRequired("name")
    productAddCmd.MarkFlagRequired("price")
    productAddCmd.MarkFlagRequired("category")
    productAddCmd.MarkFlagRequired("stock")
}
```

## 提示4：JSON数据持久化

实现JSON文件操作：

```go
func LoadInventory() error {
    if _, err := os.Stat(inventoryFile); os.IsNotExist(err) {
        // 创建默认库存
        inventory = &Inventory{
            Products:   []Product{},
            Categories: []Category{},
            NextID:     1,
        }
        return SaveInventory()
    }
    
    data, err := ioutil.ReadFile(inventoryFile)
    if err != nil {
        return err
    }
    
    return json.Unmarshal(data, &inventory)
}

func SaveInventory() error {
    data, err := json.MarshalIndent(inventory, "", "  ")
    if err != nil {
        return err
    }
    
    return ioutil.WriteFile(inventoryFile, data, 0644)
}
```

## 提示5：在命令中获取标志值

在命令执行中访问标志值：

```go
Run: func(cmd *cobra.Command, args []string) {
    name, _ := cmd.Flags().GetString("name")
    price, _ := cmd.Flags().GetFloat64("price")
    category, _ := cmd.Flags().GetString("category")
    stock, _ := cmd.Flags().GetInt("stock")
    
    product := Product{
        ID:       inventory.NextID,
        Name:     name,
        Price:    price,
        Category: category,
        Stock:    stock,
    }
    
    inventory.Products = append(inventory.Products, product)
    inventory.NextID++
    
    SaveInventory()
    fmt.Printf("✅ 产品添加成功！\n")
    fmt.Printf("ID: %d, 名称: %s, 价格: $%.2f, 分类: %s, 库存: %d\n", 
        product.ID, product.Name, product.Price, product.Category, product.Stock)
},
```

## 提示6：实现嵌套键访问

支持类似配置的点号表示法访问：

```go
func GetNestedValue(key string) (interface{}, bool) {
    parts := strings.Split(key, ".")
    
    for _, product := range inventory.Products {
        if parts[0] == "product" && len(parts) > 1 {
            // 处理 product.field 访问
            if fmt.Sprintf("%d", product.ID) == parts[1] {
                if len(parts) > 2 {
                    switch parts[2] {
                    case "name":
                        return product.Name, true
                    case "price":
                        return product.Price, true
                    // ... 其他字段
                    }
                }
                return product, true
            }
        }
    }
    
    return nil, false
}
```

## 提示7：实现搜索功能

添加搜索标志和过滤逻辑：

```go
func init() {
    searchCmd.Flags().StringP("name", "n", "", "按产品名称搜索")
    searchCmd.Flags().StringP("category", "c", "", "按分类搜索")
    searchCmd.Flags().Float64("min-price", 0, "最低价格")
    searchCmd.Flags().Float64("max-price", 0, "最高价格")
}

// 在搜索命令的 Run 函数中：
Run: func(cmd *cobra.Command, args []string) {
    name, _ := cmd.Flags().GetString("name")
    category, _ := cmd.Flags().GetString("category")
    minPrice, _ := cmd.Flags().GetFloat64("min-price")
    maxPrice, _ := cmd.Flags().GetFloat64("max-price")
    
    var results []Product
    
    for _, product := range inventory.Products {
        match := true
        
        if name != "" && !strings.Contains(strings.ToLower(product.Name), strings.ToLower(name)) {
            match = false
        }
        if category != "" && strings.ToLower(product.Category) != strings.ToLower(category) {
            match = false
        }
        if minPrice > 0 && product.Price < minPrice {
            match = false
        }
        if maxPrice > 0 && product.Price > maxPrice {
            match = false
        }
        
        if match {
            results = append(results, product)
        }
    }
    
    // 显示结果
    fmt.Printf("🔍 找到 %d 个产品:\n", len(results))
    // ... 格式化并显示结果
},
```

## 提示8：计算统计信息

实现全面的统计功能：

```go
Run: func(cmd *cobra.Command, args []string) {
    totalProducts := len(inventory.Products)
    totalCategories := len(inventory.Categories)
    
    var totalValue float64
    lowStockCount := 0
    outOfStockCount := 0
    
    for _, product := range inventory.Products {
        totalValue += product.Price * float64(product.Stock)
        
        if product.Stock == 0 {
            outOfStockCount++
        } else if product.Stock < 5 {
            lowStockCount++
        }
    }
    
    fmt.Println("📊 库存统计信息:")
    fmt.Printf("- 总产品数: %d\n", totalProducts)
    fmt.Printf("- 总分类数: %d\n", totalCategories)
    fmt.Printf("- 总价值: $%.2f\n", totalValue)
    fmt.Printf("- 低库存项 (< 5): %d\n", lowStockCount)
    fmt.Printf("- 缺货项: %d\n", outOfStockCount)
},
```

## 提示9：错误处理

在整个代码中添加适当的错误处理：

```go
func FindProductByID(id int) (*Product, int) {
    for i, product := range inventory.Products {
        if product.ID == id {
            return &product, i
        }
    }
    return nil, -1
}

// 在命令中：
product, index := FindProductByID(id)
if product == nil {
    fmt.Printf("❌ 找不到ID为 %d 的产品\n", id)
    return
}
```

## 提示10：表格格式化

创建格式美观的表格输出：

```go
func displayProductsTable(products []Product) {
    fmt.Println("📦 库存产品列表:")
    fmt.Printf("%-4s | %-15s | %-8s | %-12s | %-5s\n", "ID", "名称", "价格", "分类", "库存")
    fmt.Println("-----|-----------------|----------|--------------|-------")
    
    for _, product := range products {
        fmt.Printf("%-4d | %-15s | $%-7.2f | %-12s | %-5d\n",
            product.ID, product.Name, product.Price, product.Category, product.Stock)
    }
}
```

记得在 `init()` 函数中调用 `LoadInventory()`，并对所有文件操作进行适当的错误检查！