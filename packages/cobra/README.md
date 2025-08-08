# Cobra CLI 开发挑战

掌握使用 Cobra 库在 Go 中构建强大命令行应用程序的艺术。本项目包含 4 个循序渐进的挑战，带你从基础的 CLI 概念逐步迈向高级的生产就绪模式。

## 挑战概览

### 🎯 [挑战 1：基础 CLI 应用](./challenge-1-basic-cli/)
**难度：** 初学者 | **时长：** 30-45 分钟

通过构建一个简单的任务管理 CLI 来学习 Cobra 的基础知识，包括基本命令、版本信息和帮助系统。

**核心技能：**
- 基础 Cobra 命令结构
- 根命令设置
- 版本与关于命令
- 自动生成的帮助文本
- 命令层级基础

**涵盖主题：**
- `cobra.Command` 基础
- 命令描述与用法
- 帮助系统基础
- CLI 应用程序结构

---

### 🚀 [挑战 2：标志与参数](./challenge-2-flags-args/)
**难度：** 中级 | **时长：** 45-60 分钟

构建一个更复杂的 CLI，具备全面的标志处理、参数验证和交互功能。

**核心技能：**
- 标志类型与验证
- 位置参数
- 必需与可选标志
- 标志继承
- 自定义验证函数

**涵盖主题：**
- 持久标志与本地标志
- 标志绑定与验证
- 参数处理模式
- 错误处理与用户反馈
- 交互式 CLI 功能

---

### 📦 [挑战 3：子命令与数据持久化](./challenge-3-subcommands-persistence/)
**难度：** 中级 | **时长：** 45-60 分钟

创建一个库存管理 CLI，展示高级子命令组织结构和 JSON 数据持久化。

**核心技能：**
- 嵌套命令层级
- 通过 CLI 实现 CRUD 操作
- JSON 数据持久化
- 搜索与过滤
- 文件 I/O 操作

**涵盖主题：**
- 复杂命令结构
- 数据持久化模式
- JSON 序列化/反序列化
- 搜索功能
- 文件操作中的错误处理

---

### ⚡ [挑战 4：高级功能与中间件](./challenge-4-advanced-features/)
**难度：** 高级 | **时长：** 60-90 分钟

构建一个配置管理 CLI，展示高级 Cobra 模式，包括中间件、插件和多格式配置支持。

**核心技能：**
- 中间件系统实现
- 插件架构
- 配置管理（JSON/YAML/TOML）
- 环境变量集成
- 自定义帮助模板

**涵盖主题：**
- 命令中间件模式
- 插件系统设计
- 多种配置格式
- 验证流水线
- 高级 CLI 用户体验模式

## 学习路径

```
挑战 1：基础 CLI
        ↓
挑战 2：标志与参数  
        ↓
挑战 3：数据与子命令
        ↓  
挑战 4：高级功能
```

### 推荐前置条件
- **挑战 1：** 基础 Go 知识
- **挑战 2：** 完成挑战 1，理解数据类型
- **挑战 3：** 完成挑战 1-2，具备 JSON/文件处理经验
- **挑战 4：** 完成挑战 1-3，掌握高级 Go 模式知识

## 核心 Cobra 概念覆盖

### 核心概念
- **命令：** 构建命令层级与结构
- **标志：** 持久、本地、必需标志及自定义验证
- **参数：** 位置参数与验证
- **帮助系统：** 自定义帮助模板与文档

### 高级模式
- **中间件：** 命令执行前/后的钩子
- **插件：** 动态命令注册与插件架构
- **配置：** 支持多种格式的配置管理并集成环境变量
- **验证：** 输入验证与自定义验证器

### 生产特性
- **错误处理：** 优雅的错误管理与用户反馈
- **性能：** CLI 应用优化模式
- **安全：** 输入清理与安全实践
- **用户体验设计：** 创建直观且友好的 CLI 界面

## 挑战结构

每个挑战遵循一致的结构：

```
challenge-X-name/
├── README.md              # 挑战说明与要求
├── solution-template.go   # 包含 TODO 的模板以供实现
├── solution-template_test.go  # 全面的测试套件
├── run_tests.sh          # 测试运行脚本
├── go.mod                # 包含依赖的 Go 模块
├── metadata.json         # 挑战元数据
├── SCOREBOARD.md         # 参与者得分表
├── hints.md              # 实现提示（如有）
├── learning.md           # 额外学习资源（如有）
└── submissions/          # 参与者提交目录
```

## 开始入门

1. **根据你的经验水平选择起始挑战**
2. **阅读挑战目录中的 README.md**
3. **在 `solution-template.go` 中实现解决方案**
4. **使用 `./run_tests.sh` 测试你的解决方案**
5. **通过 PR 提交至 submissions 目录**

## 测试你的解决方案

每个挑战都包含全面的测试套件。要测试你的解决方案，请执行：

```bash
cd packages/cobra/challenge-X-name/
./run_tests.sh
```

测试脚本将：
- 提示输入你的 GitHub 用户名
- 将你的解决方案复制到临时环境
- 在你的实现上运行所有测试
- 提供详细的测试结果反馈

## 常见模式与最佳实践

### 命令结构
```go
var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "简要描述",
    Long:  "详细描述",
}

var subCmd = &cobra.Command{
    Use:   "subcmd",
    Short: "子命令描述",
    Run: func(cmd *cobra.Command, args []string) {
        // 实现逻辑
    },
}
```

### 标志处理
```go
// 持久标志（对所有子命令可用）
rootCmd.PersistentFlags().StringVar(&config, "config", "", "配置文件")

// 本地标志（仅适用于此命令）
cmd.Flags().StringVarP(&name, "name", "n", "", "名称标志")

// 必需标志
cmd.MarkFlagRequired("name")
```

### 错误处理
```go
func runCommand(cmd *cobra.Command, args []string) error {
    if err := validateInput(args); err != nil {
        return fmt.Errorf("验证失败: %w", err)
    }
    // 命令逻辑
    return nil
}
```

## 资源

- [Cobra 文档](https://cobra.dev/)
- [Cobra GitHub 仓库](https://github.com/spf13/cobra)
- [CLI 设计指南](https://clig.dev/)
- [Go CLI 最佳实践](https://blog.gopheracademy.com/advent-2017/cli-application/)

## 贡献

发现一个问题或希望改进某个挑战？欢迎贡献！

1. Fork 仓库
2. 创建功能分支
3. 进行修改
4. 如适用，添加测试
5. 提交拉取请求

---

**祝你 CLI 开发愉快！** 🚀

掌握这些挑战，成为使用 Go 和 Cobra 构建生产就绪命令行应用的高手。