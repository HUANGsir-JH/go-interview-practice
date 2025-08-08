# 挑战 4：高级功能与中间件

使用 Cobra 构建一个 **配置管理 CLI**，展示高级 CLI 模式，包括中间件、插件、配置文件和自定义帮助系统。

## 挑战要求

创建一个名为 `config-manager` 的 CLI 应用程序，用于管理应用程序配置，具备以下功能：

1. **配置管理** - 支持从多种格式（JSON、YAML、TOML）加载/保存配置
2. **中间件系统** - 命令执行前后的钩子函数
3. **插件架构** - 支持自定义命令插件
4. **环境集成** - 支持环境变量
5. **高级帮助** - 自定义帮助模板和文档
6. **验证流水线** - 支持自定义验证器的输入验证

## 预期 CLI 结构

```
config-manager                           # 根命令，带有自定义帮助
config-manager config get <key>          # 获取配置值
config-manager config set <key> <value> # 设置配置值  
config-manager config list               # 列出所有配置
config-manager config delete <key>      # 删除配置
config-manager config load <file>       # 从文件加载配置
config-manager config save <file>       # 保存配置到文件
config-manager config format <format>   # 更改配置格式 (json/yaml/toml)
config-manager plugin install <name>    # 安装插件
config-manager plugin list              # 列出已安装插件
config-manager validate                 # 验证当前配置
config-manager env sync                 # 与环境变量同步
config-manager completion bash          # 生成 Bash 补全脚本
```

## 示例输出

**设置配置（`config-manager config set database.host localhost`）：**
```
$ config-manager config set database.host localhost
🔧 配置更新成功
键：database.host
值：localhost
类型：字符串
格式：json
```

**获取配置（`config-manager config get database.host`）：**
```
$ config-manager config get database.host
📋 配置值：
键：database.host
值：localhost
类型：字符串
来源：文件
最后修改时间：2024-01-15 10:30:45
```

**加载配置（`config-manager config load app.yaml`）：**
```
$ config-manager config load app.yaml
📁 正在从 app.yaml 加载配置...
✅ 成功加载 12 个配置项
格式：yaml
验证：通过
```

**插件系统（`config-manager plugin list`）：**
```
$ config-manager plugin list
🔌 已安装插件：
名称        | 版本    | 状态   | 描述
------------|---------|--------|----------------------------------
validator   | 1.0.0   | 激活   | 高级配置验证
backup      | 0.2.1   | 激活   | 自动配置备份
generator   | 1.1.0   | 激活   | 配置模板生成器
```

## 数据模型

```go
type Config struct {
    Data     map[string]interface{} `json:"data" yaml:"data" toml:"data"`
    Format   string                 `json:"format" yaml:"format" toml:"format"`
    Version  string                 `json:"version" yaml:"version" toml:"version"`
    Metadata ConfigMetadata         `json:"metadata" yaml:"metadata" toml:"metadata"`
}

type ConfigMetadata struct {
    Created      time.Time          `json:"created" yaml:"created" toml:"created"`
    Modified     time.Time          `json:"modified" yaml:"modified" toml:"modified"`
    Source       string             `json:"source" yaml:"source" toml:"source"`
    Validation   ValidationResult   `json:"validation" yaml:"validation" toml:"validation"`
    Environment  map[string]string  `json:"environment" yaml:"environment" toml:"environment"`
}

type Plugin struct {
    Name        string            `json:"name"`
    Version     string            `json:"version"`
    Status      string            `json:"status"`
    Description string            `json:"description"`
    Commands    []PluginCommand   `json:"commands"`
    Config      map[string]string `json:"config"`
}

type ValidationResult struct {
    Valid   bool     `json:"valid"`
    Errors  []string `json:"errors"`
    Warnings []string `json:"warnings"`
}
```

## 实现要求

### 配置管理
- 支持 JSON、YAML 和 TOML 格式
- 支持嵌套键访问（如 `database.host`、`server.port`）
- 类型保留（字符串、整数、布尔值、浮点数）
- 支持原子更新及回滚能力

### 中间件系统
- 命令执行前的验证中间件
- 命令执行后的审计日志中间件
- 配置备份中间件
- 性能监控中间件

### 插件架构
- 动态插件加载
- 插件命令注册
- 插件配置管理
- 插件生命周期管理（安装/卸载/启用/禁用）

### 环境集成
- 环境变量映射
- 变量优先级处理
- 自动同步功能
- 环境验证

### 高级帮助系统
- 自定义帮助模板
- 交互式帮助模式
- 示例生成
- 带描述的命令补全

### 验证流水线
- 模式验证
- 自定义验证函数
- 依赖验证
- 环境特定验证

## 技术要求

### 中间件实现
```go
type Middleware func(*cobra.Command, []string) error

// 执行于命令前的 PreRun 中间件
func ValidationMiddleware(cmd *cobra.Command, args []string) error {
    // 在命令执行前验证配置
}

// 执行于命令后的 PostRun 中间件
func AuditMiddleware(cmd *cobra.Command, args []string) error {
    // 为审计记录命令执行情况
}
```

### 插件接口
```go
type PluginInterface interface {
    Initialize() error
    GetCommands() []*cobra.Command
    GetInfo() PluginInfo
    Cleanup() error
}
```

### 配置格式检测
- 根据文件扩展名自动检测格式
- 基于内容的格式检测
- 格式转换工具
- 不同格式间的迁移支持

## 测试要求

你的解决方案必须通过以下测试：
- 所有格式下的配置增删改查操作
- 中间件的执行顺序与功能
- 插件加载与命令注册
- 环境变量集成
- 包含自定义验证器的验证流水线
- 帮助系统的自定义功能
- 格式转换与迁移
- 错误处理与恢复
- 并发访问保护
- 性能基准测试

## 高级功能

### 自定义帮助模板
- 支持颜色的丰富格式化
- 交互式示例
- 上下文感知的帮助
- 多语言支持

### 性能优化
- 配置的延迟加载
- 缓存机制
- 大配置的流式处理
- 内存高效的运算

### 安全特性
- 配置加密
- 访问控制
- 审计日志
- 安全的插件加载

本挑战测试对高级 Cobra 模式的掌握，并展示生产级别的 CLI 应用架构。