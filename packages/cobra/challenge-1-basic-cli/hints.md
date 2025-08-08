# 挑战1：基础CLI应用程序提示

## 提示1：设置根命令

根命令已为您创建。您需要实现 `Run` 函数：

```go
Run: func(cmd *cobra.Command, args []string) {
    cmd.Help()  // 当未提供子命令时显示帮助信息
},
```

## 提示2：实现版本命令

对于版本命令，请打印出期望的精确格式：

```go
Run: func(cmd *cobra.Command, args []string) {
    fmt.Printf("taskcli 版本 %s\n", version)
    fmt.Println("使用 ❤️ 构建于 Cobra")
},
```

## 提示3：实现关于命令

对于关于命令，请包含所有必需的信息：

```go
Run: func(cmd *cobra.Command, args []string) {
    fmt.Printf("任务管理器 CLI v%s\n\n", version)
    fmt.Println("一个简单高效的任务管理工具，使用 Go 和 Cobra 构建。")
    fmt.Println("非常适合从命令行管理您的日常任务。")
    fmt.Println()
    fmt.Println("作者：您的名字")
    fmt.Println("仓库：https://github.com/example/taskcli")
    fmt.Println("许可证：MIT")
},
```

## 提示4：将命令添加到根命令

在 `init()` 函数中添加子命令：

```go
func init() {
    rootCmd.AddCommand(versionCmd)
    rootCmd.AddCommand(aboutCmd)
}
```

## 提示5：主函数

主函数应执行根命令并处理错误：

```go
func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintf(os.Stderr, "错误：%v\n", err)
        os.Exit(1)
    }
}
```

## 提示6：命令结构

Cobra 自动添加：
- `help` 命令用于显示帮助
- `completion` 命令用于 shell 补全
- 所有命令均支持 `-h, --help` 标志

您只需实现 `version` 和 `about` 命令。

## 提示7：测试您的实现

在本地运行您的CLI进行测试：

```bash
go run . 
go run . version
go run . about
go run . help
go run . help version
```