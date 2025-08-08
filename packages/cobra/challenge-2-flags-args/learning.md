# 学习：高级Cobra CLI - 标志和参数

## 🌟 **什么是CLI标志和参数？**

命令行接口使用**标志**和**参数**来接收用户输入并配置程序行为。正确处理这些内容对于构建专业的CLI工具至关重要。

### **标志与参数的区别**
- **标志**：可选的命名参数，用于修改行为（`--verbose`，`--format json`）
- **参数**：位置参数，用于提供数据（`copy source.txt dest.txt`）

## 🏗️ **核心概念**

### **1. 标志类型**

Cobra支持多种标志类型以处理不同的数据：

```go
// 布尔标志（true/false）
var verbose bool
cmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "启用详细输出")

// 字符串标志
var format string
cmd.Flags().StringVar(&format, "format", "table", "输出格式")

// 整数标志
var size int
cmd.Flags().IntVar(&size, "size", 0, "文件大小（字节）")

// 字符串切片标志（多个值）
var tags []string
cmd.Flags().StringSliceVar(&tags, "tags", []string{}, "文件标签")
```

### **2. 全局标志与命令特定标志**

**全局标志**（对所有命令可用）：
```go
// 添加到根命令
rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "启用详细输出")
```

**命令特定标志**（仅对一个命令可用）：
```go
// 添加到特定命令
listCmd.Flags().StringVar(&format, "format", "table", "输出格式")
```

### **3. 必需标志与可选标志**

```go
// 必需标志
createCmd.Flags().StringVar(&name, "name", "", "文件名（必需）")
createCmd.MarkFlagRequired("name")

// 可选标志并带默认值
listCmd.Flags().StringVar(&format, "format", "table", "输出格式")
```

## 📐 **参数验证**

Cobra 提供了内置的命令参数验证器：

### **常用验证器**
```go
// 精确 N 个参数
var copyCmd = &cobra.Command{
    Use:  "copy <source> <destination>",
    Args: cobra.ExactArgs(2),
}

// 至少 N 个参数
var processCmd = &cobra.Command{
    Use:  "process <file1> [file2...]",
    Args: cobra.MinimumNArgs(1),
}

// 最多 N 个参数
var listCmd = &cobra.Command{
    Use:  "list [directory]",
    Args: cobra.MaximumNArgs(1),
}

// 参数范围
var mergeCmd = &cobra.Command{
    Use:  "merge <files...>",
    Args: cobra.RangeArgs(2, 5),
}

// 无参数
var statusCmd = &cobra.Command{
    Use:  "status",
    Args: cobra.NoArgs,
}
```

### **自定义参数验证**
```go
var customCmd = &cobra.Command{
    Use: "custom",
    Args: func(cmd *cobra.Command, args []string) error {
        if len(args) < 1 {
            return fmt.Errorf("至少需要 1 个参数")
        }
        
        for _, arg := range args {
            if !strings.HasSuffix(arg, ".txt") {
                return fmt.Errorf("所有参数必须是 .txt 文件")
            }
        }
        
        return nil
    },
}
```

## 🎯 **标志绑定与变量**

### **变量绑定**
标志可以绑定到变量以便轻松访问：

```go
var config struct {
    Verbose bool
    Format  string
    Size    int
}

func init() {
    rootCmd.PersistentFlags().BoolVar(&config.Verbose, "verbose", false, "详细输出")
    listCmd.Flags().StringVar(&config.Format, "format", "table", "输出格式")
    createCmd.Flags().IntVar(&config.Size, "size", 0, "文件大小")
}
```

### **标志别名（短形式和长形式）**
```go
// --verbose 和 -v 都有效
cmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "启用详细输出")

// --format 和 -f 都有效  
cmd.Flags().StringVarP(&format, "format", "f", "table", "输出格式")
```

## 🔧 **高级标志功能**

### **标志依赖关系**
```go
func init() {
    cmd.Flags().StringVar(&username, "username", "", "用户名")
    cmd.Flags().StringVar(&password, "password", "", "密码")
    
    // 如果提供了用户名，则密码为必需
    cmd.MarkFlagsRequiredTogether("username", "password")
    
    // 这些标志不能同时使用
    cmd.MarkFlagsMutuallyExclusive("username", "token")
}
```

### **标志值验证**
```go
func init() {
    cmd.Flags().StringVar(&format, "format", "table", "输出格式")
    
    // 验证标志值
    cmd.RegisterFlagCompletionFunc("format", func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
        return []string{"json", "table", "csv"}, cobra.ShellCompDirectiveNoFileComp
    })
}

func validateFormat(cmd *cobra.Command, args []string) error {
    validFormats := []string{"json", "table", "csv"}
    for _, valid := range validFormats {
        if format == valid {
            return nil
        }
    }
    return fmt.Errorf("无效格式: %s (有效: %s)", format, strings.Join(validFormats, ", "))
}
```

## 💡 **命令结构最佳实践**

### **一致的命令处理器模式**
```go
func commandHandler(cmd *cobra.Command, args []string) error {
    // 1. 验证输入
    if err := validateInputs(args); err != nil {
        return err
    }
    
    // 2. 处理全局标志
    if verbose {
        fmt.Printf("使用参数执行命令: %v\n", args)
    }
    
    // 3. 执行主逻辑
    result, err := doWork(args)
    if err != nil {
        return fmt.Errorf("操作失败: %w", err)
    }
    
    // 4. 格式化并输出结果
    return outputResult(result)
}
```

### **错误处理策略**
```go
func processFile(cmd *cobra.Command, args []string) error {
    filename := args[0]
    
    // 检查文件是否存在
    if _, err := os.Stat(filename); os.IsNotExist(err) {
        return fmt.Errorf("文件 %s 不存在", filename)
    }
    
    // 处理文件
    if err := doProcessing(filename); err != nil {
        return fmt.Errorf("无法处理 %s: %w", filename, err)
    }
    
    // 成功消息
    if verbose {
        fmt.Printf("成功处理: %s\n", filename)
    }
    
    return nil
}
```

## 📊 **输出格式化模式**

### **JSON 与人类可读输出**
```go
type Response struct {
    Success bool        `json:"success"`
    Message string      `json:"message,omitempty"`
    Data    interface{} `json:"data,omitempty"`
    Error   string      `json:"error,omitempty"`
}

func outputResult(data interface{}) error {
    if format == "json" {
        response := Response{
            Success: true,
            Data:    data,
        }
        
        jsonData, err := json.MarshalIndent(response, "", "  ")
        if err != nil {
            return err
        }
        
        fmt.Println(string(jsonData))
        return nil
    }
    
    // 人类可读格式
    return outputTable(data)
}
```

### **表格格式化**
```go
func outputTable(files []FileInfo) error {
    // 表头
    fmt.Printf("%-30s %-10s %-20s %s\n", "名称", "大小", "修改时间", "类型")
    fmt.Println(strings.Repeat("-", 75))
    
    // 行
    for _, file := range files {
        fileType := "文件"
        if file.IsDir {
            fileType = "目录"
        }
        
        fmt.Printf("%-30s %-10d %-20s %s\n", 
            truncate(file.Name, 30),
            file.Size,
            file.ModTime.Format("2006-01-02 15:04:05"),
            fileType,
        )
    }
    
    return nil
}

func truncate(s string, maxLen int) string {
    if len(s) <= maxLen {
        return s
    }
    return s[:maxLen-3] + "..."
}
```

## 🧪 **测试CLI应用程序**

### **命令测试模式**
```go
func TestCommand(t *testing.T) {
    // 设置
    cmd := &cobra.Command{
        Use: "test",
        RunE: func(cmd *cobra.Command, args []string) error {
            // 你的命令逻辑
            return nil
        },
    }
    
    // 捕获输出
    buf := new(bytes.Buffer)
    cmd.SetOut(buf)
    cmd.SetErr(buf)
    cmd.SetArgs([]string{"arg1", "arg2"})
    
    // 执行
    err := cmd.Execute()
    
    // 断言
    assert.NoError(t, err)
    assert.Contains(t, buf.String(), "预期输出")
}
```

### **标志测试**
```go
func TestFlags(t *testing.T) {
    var verbose bool
    var format string
    
    cmd := &cobra.Command{Use: "test"}
    cmd.Flags().BoolVar(&verbose, "verbose", false, "详细输出")
    cmd.Flags().StringVar(&format, "format", "table", "输出格式")
    
    // 测试标志解析
    cmd.SetArgs([]string{"--verbose", "--format", "json"})
    err := cmd.Execute()
    
    assert.NoError(t, err)
    assert.True(t, verbose)
    assert.Equal(t, "json", format)
}
```

## 🚀 **真实世界示例**

### **专业CLI工具**
了解流行工具如何使用标志和参数：

**Docker:**
```bash
docker run -d --name myapp -p 8080:80 nginx:latest
# -d: 后台运行模式（布尔标志）
# --name: 容器名称（字符串标志）  
# -p: 端口映射（字符串标志）
# nginx:latest: 镜像参数
```

**kubectl:**
```bash
kubectl get pods --namespace production --output json
# get: 子命令
# pods: 参数  
# --namespace: 字符串标志
# --output: 字符串标志
```

**git:**
```bash
git commit -m "message" --author "name <email>"
# commit: 子命令
# -m: 消息标志（字符串）
# --author: 作者标志（字符串）
```

### **文件管理CLI示例**
```bash
# 全局详细标志
filecli --verbose list

# 命令特定格式标志
filecli list --format json /home/user

# 必需的安全标志
filecli delete --force important.txt

# 多个标志和参数
filecli copy --preserve-permissions source.txt backup.txt
```

## 🎨 **高级模式**

### **命令链式调用与管道**
```go
// 支持命令链式调用
var chainCmd = &cobra.Command{
    Use: "chain",
    PreRunE: func(cmd *cobra.Command, args []string) error {
        // 验证前置条件
        return nil
    },
    RunE: func(cmd *cobra.Command, args []string) error {
        // 主要执行
        return nil
    },
    PostRunE: func(cmd *cobra.Command, args []string) error {
        // 清理或后续操作
        return nil
    },
}
```

### **动态命令生成**
```go
func generateCommands() {
    for _, service := range services {
        cmd := &cobra.Command{
            Use:   service.Name,
            Short: fmt.Sprintf("管理 %s 服务", service.Name),
            RunE:  createServiceHandler(service),
        }
        
        // 添加服务特定标志
        for _, flag := range service.Flags {
            cmd.Flags().StringVar(&flag.Value, flag.Name, flag.Default, flag.Help)
        }
        
        rootCmd.AddCommand(cmd)
    }
}
```

## 📚 **关键要点**

1. **标志设计**：使用清晰、一致的命名约定
2. **验证**：尽早验证输入并提供有用的错误信息  
3. **文档**：为所有标志和命令编写描述性帮助文本
4. **测试**：测试所有标志组合和边界情况
5. **用户体验**：在适当情况下提供短标志和长标志形式
6. **错误处理**：返回具有可操作指导意义的有意义错误
7. **输出格式化**：支持机器可读（JSON）和人类可读格式

## 🔗 **进一步阅读**

- [Cobra 文档](https://github.com/spf13/cobra)
- [12-Factor CLI 应用](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)
- [命令行界面指南](https://clig.dev/)
- [POSIX 工具约定](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)