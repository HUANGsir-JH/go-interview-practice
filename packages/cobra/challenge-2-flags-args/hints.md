# 挑战2提示：高级标志和参数

## 提示1：设置根命令

从基本的Cobra根命令结构开始：

```go
var rootCmd = &cobra.Command{
    Use:   "filecli",
    Short: "一个文件管理CLI工具",
    Long:  `一个演示Cobra高级标志和参数处理的文件管理器CLI。`,
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}
```

## 提示2：添加全局标志

全局标志对所有命令都可用。使用 `PersistentFlags()` 将它们添加到根命令中：

```go
func init() {
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "启用详细输出")
}
```

`BoolVarP` 函数参数：
- `&verbose`：存储标志值的变量指针
- `"verbose"`：长标志名（--verbose）
- `"v"`：短标志名（-v）
- `false`：默认值
- `"启用详细输出"`：帮助文本

## 提示3：命令特定标志

使用 `Flags()` 为特定命令添加仅在该命令中可用的标志：

```go
func init() {
    listCmd.Flags().StringVar(&format, "format", "table", "输出格式 (json, table)")
}
```

## 提示4：必需标志

使用 `MarkFlagRequired()` 使标志变为必需：

```go
func init() {
    deleteCmd.Flags().BoolVar(&force, "force", false, "强制删除（必需）")
    deleteCmd.MarkFlagRequired("force")
    
    createCmd.Flags().StringVar(&name, "name", "", "文件名（必需）")
    createCmd.MarkFlagRequired("name")
}
```

## 提示5：参数验证

使用Cobra内置的参数验证器：

```go
var copyCmd = &cobra.Command{
    Use:  "copy <source> <destination>",
    Args: cobra.ExactArgs(2), // 要求恰好有2个参数
    RunE: copyFile,
}

var listCmd = &cobra.Command{
    Use:  "list [directory]",
    Args: cobra.MaximumNArgs(1), // 可选参数（0或1个）
    RunE: listFiles,
}

var deleteCmd = &cobra.Command{
    Use:  "delete <file>",
    Args: cobra.ExactArgs(1), // 要求恰好有1个参数
    RunE: deleteFile,
}
```

常见参数验证器：
- `cobra.ExactArgs(n)`：恰好n个参数
- `cobra.MinimumNArgs(n)`：至少n个参数
- `cobra.MaximumNArgs(n)`：最多n个参数
- `cobra.RangeArgs(min, max)`：介于min和max之间的参数数量
- `cobra.NoArgs`：不允许任何参数

## 提示6：命令实现模式

保持命令处理器的一致性结构：

```go
func listFiles(cmd *cobra.Command, args []string) error {
    // 从参数获取目录，或使用默认值
    dir := "."
    if len(args) > 0 {
        dir = args[0]
    }

    // 使用全局verbose标志
    if verbose {
        fmt.Printf("正在列出目录中的文件：%s\n", dir)
    }

    // 在此处实现你的逻辑
    files, err := readDirectory(dir)
    if err != nil {
        return err
    }

    // 处理格式标志
    if format == "json" {
        return formatAsJSON(files)
    } else {
        formatAsTable(files)
    }

    return nil
}
```

## 提示7：标志类型与绑定

Cobra支持多种标志类型：

```go
// 字符串标志
cmd.Flags().StringVar(&stringVar, "name", "default", "帮助文本")

// 整数标志
cmd.Flags().IntVar(&intVar, "size", 0, "帮助文本")

// 布尔标志
cmd.Flags().BoolVar(&boolVar, "force", false, "帮助文本")

// 字符串切片标志
cmd.Flags().StringSliceVar(&sliceVar, "tags", []string{}, "帮助文本")
```

## 提示8：将命令添加到根命令

别忘了将子命令添加到根命令中：

```go
func init() {
    rootCmd.AddCommand(listCmd)
    rootCmd.AddCommand(copyCmd)
    rootCmd.AddCommand(deleteCmd)
    rootCmd.AddCommand(createCmd)
}
```

## 提示9：错误处理最佳实践

返回有意义的错误，并使用 `RunE` 而不是 `Run`：

```go
func deleteFile(cmd *cobra.Command, args []string) error {
    filename := args[0]

    // 检查文件是否存在
    if !fileExists(filename) {
        return fmt.Errorf("文件 %s 不存在", filename)
    }

    // 执行操作
    if err := os.Remove(filename); err != nil {
        return fmt.Errorf("无法删除文件 %s: %w", filename, err)
    }

    if verbose {
        fmt.Printf("已成功删除：%s\n", filename)
    }

    return nil
}
```

## 提示10：验证辅助函数

为常见的验证模式创建辅助函数：

```go
func validateFileName(filename string) error {
    if filename == "" {
        return fmt.Errorf("文件名不能为空")
    }
    
    if strings.ContainsAny(filename, "/\\:*?\"<>|") {
        return fmt.Errorf("文件名包含无效字符")
    }
    
    return nil
}

func fileExists(filename string) bool {
    _, err := os.Stat(filename)
    return !os.IsNotExist(err)
}
```

## 提示11：JSON与表格输出

实现灵活的输出格式化：

```go
func formatAsJSON(data interface{}) error {
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

func formatAsTable(files []FileInfo) {
    fmt.Printf("%-30s %-10s %-20s %s\n", "NAME", "SIZE", "MODIFIED", "TYPE")
    fmt.Println(strings.Repeat("-", 70))
    
    for _, file := range files {
        fileType := "FILE"
        if file.IsDir {
            fileType = "DIR"
        }
        
        fmt.Printf("%-30s %-10d %-20s %s\n", 
            file.Name, 
            file.Size, 
            file.ModTime.Format("2006-01-02 15:04:05"),
            fileType,
        )
    }
}
```

## 提示12：测试你的实现

使用各种标志组合测试你的CLI：

```bash
# 测试全局标志
./filecli --verbose list

# 测试命令特定标志
./filecli list --format json
./filecli list --format table

# 测试必需标志
./filecli delete myfile.txt --force
./filecli create --name "newfile.txt" --size 100

# 测试参数
./filecli copy source.txt destination.txt
./filecli list /path/to/directory
```

## 常见陷阱避免

1. **忘记将命令添加到根命令**：使用 `rootCmd.AddCommand()`
2. **未处理verbose标志**：在处理器中检查 `verbose` 变量
3. **参数验证不正确**：使用适当的 `cobra.Args` 验证器
4. **缺少必需标志验证**：使用 `MarkFlagRequired()`
5. **错误信息不佳**：返回带上下文的描述性错误