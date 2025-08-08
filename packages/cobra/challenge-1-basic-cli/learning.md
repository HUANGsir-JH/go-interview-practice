# 学习：Cobra CLI 框架基础

## 🌟 **什么是 Cobra？**

Cobra 是一个用于在 Go 语言中创建现代命令行界面的强大库。它被许多流行的 CLI 工具使用，包括 Docker、Kubernetes、Hugo 和 GitHub CLI。

### **为什么选择 Cobra？**
- **功能强大**：轻松创建具有子命令的复杂 CLI 应用
- **用户友好**：自动生成帮助文档、Shell 补全和手册页
- **灵活**：支持标志、参数和嵌套命令
- **经过充分测试**：被大型项目在生产环境中广泛验证
- **符合 POSIX 标准**：遵循标准 CLI 约定

## 🏗️ **核心概念**

### **1. 命令**
命令是 CLI 应用的核心构建模块。每个命令可以包含：
- 名称（例如 "version"、"about"）
- 简短和长描述
- 执行函数
- 子命令
- 标志和参数

```go
var myCmd = &cobra.Command{
    Use:   "mycommand",
    Short: "简要描述",
    Long:  "更详细的描述，说明此命令的功能",
    Run: func(cmd *cobra.Command, args []string) {
        // 命令实现
    },
}
```

### **2. 根命令**
根命令是你的 CLI 应用的主要入口点：

```go
var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "我的应用能完成惊人的事情",
}
```

### **3. 子命令**
你可以添加子命令来创建分层的 CLI 结构：

```go
rootCmd.AddCommand(versionCmd)
rootCmd.AddCommand(configCmd)
```

## 📖 **命令结构**

### **命令层级**
```
myapp                    # 根命令
├── version             # 子命令
├── config              # 子命令
│   ├── set            # 子子命令
│   └── get            # 子子命令
└── help               # 自动生成
```

### **命令属性**
- **Use**：命令名称和语法
- **Short**：简要描述（在命令列表中显示）
- **Long**：详细描述（在帮助信息中显示）
- **Example**：使用示例
- **Run**：调用命令时执行的函数

## 🔧 **构建你的第一个 CLI**

### **步骤 1：创建根命令**
```go
var rootCmd = &cobra.Command{
    Use:   "taskcli",
    Short: "任务管理器 CLI",
    Long:  "一个强大的命令行任务管理工具",
}
```

### **步骤 2：添加子命令**
```go
var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "显示版本信息",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("taskcli 版本 1.0.0")
    },
}

func init() {
    rootCmd.AddCommand(versionCmd)
}
```

### **步骤 3：执行**
```go
func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
```

## 🎯 **自动生成的功能**

### **帮助系统**
Cobra 自动生成：
- `help` 命令
- 所有命令的 `-h, --help` 标志
- 格式化的帮助文本，包含描述
- 使用说明

### **补全功能**
Cobra 提供以下 Shell 补全支持：
- Bash
- Zsh
- Fish
- PowerShell

### **错误处理**
Cobra 提供内置错误处理功能，包括：
- 未知命令
- 无效标志
- 缺少必需参数

## 💡 **最佳实践**

### **1. 命令命名**
- 使用清晰、描述性的名称
- 遵循 动词-名词 模式（例如 `list tasks`、`create user`）
- 保持名称简短但有意义

### **2. 描述信息**
- 为命令列表编写有用的简短描述
- 提供包含示例的详细长描述
- 在有帮助时提供使用示例

### **3. 错误消息**
- 提供清晰、可操作的错误信息
- 尽可能建议正确的用法
- 使用一致的错误格式

### **4. 输出格式**
- 使用一致的输出格式
- 考虑为自动化提供结构化输出（JSON/YAML）
- 默认提供人类可读的输出

## 🚀 **高级功能**

### **PreRun 钩子**
在命令运行前执行代码：
```go
PreRun: func(cmd *cobra.Command, args []string) {
    // 设置或验证代码
},
```

### **持久性标志**
可在命令及其所有子命令中使用的标志：
```go
rootCmd.PersistentFlags().StringVar(&configFile, "config", "", "配置文件")
```

### **必选命令**
使子命令成为必选：
```go
cmd.MarkFlagRequired("name")
```

## 📚 **真实世界示例**

### **Docker CLI 结构**
```
docker
├── build
├── run
├── ps
├── images
└── system
    ├── df
    └── prune
```

### **Kubernetes CLI 结构**
```
kubectl
├── get
├── create
├── apply
├── delete
└── config
    ├── view
    └── set-context
```

## 🔗 **资源**

- [官方 Cobra 文档](https://cobra.dev/)
- [Cobra GitHub 仓库](https://github.com/spf13/cobra)
- [Cobra 生成器](https://github.com/spf13/cobra-cli)
- [CLI 设计指南](https://clig.dev/)

## 🎪 **常见模式**

### **版本命令**
每个 CLI 都应包含一个版本命令：
```go
var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "打印版本信息",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Printf("%s 版本 %s\n", appName, version)
    },
}
```

### **配置命令**
许多 CLI 需要配置管理：
```go
var configCmd = &cobra.Command{
    Use:   "config",
    Short: "管理配置",
}
```

### **列表命令**
列出资源的常见模式：
```go
var listCmd = &cobra.Command{
    Use:   "list",
    Short: "列出项目",
    Run: func(cmd *cobra.Command, args []string) {
        // 列出实现
    },
}