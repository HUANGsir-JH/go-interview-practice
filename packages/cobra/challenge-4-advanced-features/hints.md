# 挑战4提示：高级功能与中间件

## 提示1：使用中间件配置根命令

为config-manager CLI配置中间件支持：

```go
var rootCmd = &cobra.Command{
    Use:   "config-manager",
    Short: "配置管理CLI - 支持插件和中间件的高级配置管理",
    Long:  "一个强大的配置管理系统，支持多种格式、中间件、插件和环境集成。",
    PersistentPreRun: func(cmd *cobra.Command, args []string) {
        // 在任何命令执行前执行中间件
        ApplyMiddleware(cmd, args)
    },
    PersistentPostRun: func(cmd *cobra.Command, args []string) {
        // 命令执行后清理
        if err := SaveConfig(); err != nil {
            fmt.Printf("警告：保存配置失败: %v\n", err)
        }
    },
}
```

## 提示2：实现中间件系统

创建中间件流水线：

```go
type Middleware func(*cobra.Command, []string) error

var middlewares []Middleware

func ApplyMiddleware(cmd *cobra.Command, args []string) error {
    for _, middleware := range middlewares {
        if err := middleware(cmd, args); err != nil {
            return fmt.Errorf("中间件执行失败: %w", err)
        }
    }
    return nil
}

// 验证中间件
func ValidationMiddleware(cmd *cobra.Command, args []string) error {
    result := ValidateConfiguration()
    if !result.Valid && len(result.Errors) > 0 {
        fmt.Printf("⚠️  配置警告: %v\n", result.Warnings)
    }
    return nil
}

// 审计中间件
func AuditMiddleware(cmd *cobra.Command, args []string) error {
    timestamp := time.Now().Format("2006-01-02 15:04:05")
    fmt.Printf("🔍 [%s] 执行中: %s %v\n", timestamp, cmd.Name(), args)
    return nil
}
```

## 提示3：使用点号表示法访问嵌套键

实现使用点号表示法的配置键访问：

```go
func GetNestedValue(key string) (interface{}, bool) {
    if config == nil || config.Data == nil {
        return nil, false
    }
    
    parts := strings.Split(key, ".")
    current := config.Data
    
    for i, part := range parts {
        if value, exists := current[part]; exists {
            if i == len(parts)-1 {
                // 最后一部分，返回值
                return value, true
            }
            
            // 如果是map则继续深入
            if nestedMap, ok := value.(map[string]interface{}); ok {
                current = nestedMap
            } else {
                return nil, false
            }
        } else {
            return nil, false
        }
    }
    
    return nil, false
}

func SetNestedValue(key string, value interface{}) error {
    if config == nil {
        config = &Config{
            Data:     make(map[string]interface{}),
            Format:   "json",
            Version:  "1.0.0",
            Metadata: ConfigMetadata{},
        }
    }
    
    parts := strings.Split(key, ".")
    current := config.Data
    
    // 导航到目标键的父级
    for i, part := range parts[:len(parts)-1] {
        if _, exists := current[part]; !exists {
            current[part] = make(map[string]interface{})
        }
        
        if nestedMap, ok := current[part].(map[string]interface{}); ok {
            current = nestedMap
        } else {
            return fmt.Errorf("无法设置嵌套值: %s 不是映射类型", strings.Join(parts[:i+1], "."))
        }
    }
    
    // 设置最终值
    current[parts[len(parts)-1]] = value
    config.Metadata.Modified = time.Now()
    
    return nil
}
```

## 提示4：多格式配置支持

实现格式检测与转换：

```go
func DetectFormat(filename string) string {
    ext := strings.ToLower(filepath.Ext(filename))
    switch ext {
    case ".yaml", ".yml":
        return "yaml"
    case ".toml":
        return "toml"
    case ".json":
        return "json"
    default:
        return "json" // 默认回退
    }
}

func ConvertFormat(targetFormat string) error {
    if config.Format == targetFormat {
        return nil // 已经是目标格式
    }
    
    // 更新格式元数据
    config.Format = targetFormat
    config.Metadata.Modified = time.Now()
    
    return nil
}

func LoadConfigFromFile(filename string) error {
    data, err := ioutil.ReadFile(filename)
    if err != nil {
        return fmt.Errorf("读取文件失败: %w", err)
    }
    
    format := DetectFormat(filename)
    
    switch format {
    case "json":
        err = json.Unmarshal(data, config)
    case "yaml":
        err = yaml.Unmarshal(data, config)
    case "toml":
        // 如需添加TOML支持
        return fmt.Errorf("TOML格式尚未实现")
    default:
        return fmt.Errorf("不支持的格式: %s", format)
    }
    
    if err != nil {
        return fmt.Errorf("解析 %s 失败: %w", format, err)
    }
    
    config.Metadata.Source = filename
    config.Metadata.Modified = time.Now()
    
    return nil
}
```

## 提示5：插件系统实现

创建基本的插件架构：

```go
type PluginInterface interface {
    Initialize() error
    GetCommands() []*cobra.Command
    GetInfo() PluginInfo
    Cleanup() error
}

type PluginInfo struct {
    Name        string
    Version     string
    Description string
}

func RegisterPlugin(plugin Plugin) error {
    // 检查插件是否已存在
    for _, existing := range plugins {
        if existing.Name == plugin.Name {
            return fmt.Errorf("插件 %s 已注册", plugin.Name)
        }
    }
    
    // 添加到插件注册表
    plugins = append(plugins, plugin)
    
    fmt.Printf("✅ 插件 '%s' v%s 注册成功\n", plugin.Name, plugin.Version)
    return nil
}

// 模拟插件安装
func InstallPlugin(name string) error {
    // 在真实实现中，这会下载并安装插件
    plugin := Plugin{
        Name:        name,
        Version:     "1.0.0",
        Status:      "active",
        Description: fmt.Sprintf("模拟插件: %s", name),
        Commands:    []PluginCommand{},
        Config:      make(map[string]string),
    }
    
    return RegisterPlugin(plugin)
}
```

## 提示6：环境变量集成

实现环境变量同步：

```go
func SyncWithEnvironment() error {
    if config.Metadata.Environment == nil {
        config.Metadata.Environment = make(map[string]string)
    }
    
    // 定义要同步的环境变量前缀
    prefixes := []string{"CONFIG_", "APP_"}
    
    for _, prefix := range prefixes {
        for _, env := range os.Environ() {
            pair := strings.SplitN(env, "=", 2)
            if len(pair) == 2 && strings.HasPrefix(pair[0], prefix) {
                key := strings.TrimPrefix(pair[0], prefix)
                key = strings.ToLower(strings.ReplaceAll(key, "_", "."))
                
                // 存储在环境追踪中
                config.Metadata.Environment[pair[0]] = pair[1]
                
                // 设置到配置中
                SetNestedValue(key, pair[1])
            }
        }
    }
    
    config.Metadata.Modified = time.Now()
    return nil
}
```

## 提示7：验证流水线

实现全面的配置验证：

```go
func ValidateConfiguration() ValidationResult {
    result := ValidationResult{
        Valid:    true,
        Errors:   []string{},
        Warnings: []string{},
    }
    
    if config == nil || config.Data == nil {
        result.Valid = false
        result.Errors = append(result.Errors, "配置为空")
        return result
    }
    
    // 验证必填字段
    requiredFields := []string{"app.name", "app.version"}
    for _, field := range requiredFields {
        if _, exists := GetNestedValue(field); !exists {
            result.Warnings = append(result.Warnings, fmt.Sprintf("建议字段 %s 缺失", field))
        }
    }
    
    // 验证数据类型
    if port, exists := GetNestedValue("server.port"); exists {
        if portStr, ok := port.(string); ok {
            if _, err := strconv.Atoi(portStr); err != nil {
                result.Valid = false
                result.Errors = append(result.Errors, "server.port 必须是有效整数")
            }
        }
    }
    
    return result
}
```

## 提示8：自定义帮助模板

设置自定义帮助格式：

```go
func SetCustomHelpTemplate() {
    helpTemplate := `{{with (or .Long .Short)}}{{. | trimTrailingWhitespaces}}

{{end}}{{if or .Runnable .HasSubCommands}}{{.UsageString}}{{end}}`
    
    cobra.AddTemplateFunc("StyleHeading", func(s string) string {
        return fmt.Sprintf("\033[1;36m%s\033[0m", s) // 青色粗体
    })
    
    rootCmd.SetHelpTemplate(helpTemplate)
}
```

## 提示9：使用Viper集成进行配置加载

使用Viper实现高级配置管理：

```go
func LoadConfig() error {
    viper.SetConfigName("config")
    viper.SetConfigType("json")
    viper.AddConfigPath(".")
    viper.AddConfigPath("$HOME/.config-manager")
    
    // 环境变量支持
    viper.AutomaticEnv()
    viper.SetEnvPrefix("CONFIG")
    viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
    
    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); ok {
            // 配置文件未找到；创建默认配置
            return createDefaultConfig()
        } else {
            return fmt.Errorf("读取配置文件错误: %w", err)
        }
    }
    
    // 反序列化到我们的配置结构
    var tempData map[string]interface{}
    if err := viper.Unmarshal(&tempData); err != nil {
        return fmt.Errorf("反序列化配置错误: %w", err)
    }
    
    config = &Config{
        Data:     tempData,
        Format:   "json",
        Version:  "1.0.0",
        Metadata: ConfigMetadata{
            Created:  time.Now(),
            Modified: time.Now(),
            Source:   viper.ConfigFileUsed(),
        },
    }
    
    return nil
}
```

## 提示10：命令实现示例

实现关键命令：

```go
// 配置获取命令
var configGetCmd = &cobra.Command{
    Use:   "get <key>",
    Short: "通过键获取配置值",
    Args:  cobra.ExactArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        key := args[0]
        value, exists := GetNestedValue(key)
        
        if !exists {
            fmt.Printf("❌ 键 '%s' 未找到\n", key)
            return
        }
        
        fmt.Printf("📋 配置值:\n")
        fmt.Printf("键: %s\n", key)
        fmt.Printf("值: %v\n", value)
        fmt.Printf("类型: %T\n", value)
        fmt.Printf("来源: %s\n", config.Metadata.Source)
        fmt.Printf("最后修改时间: %s\n", config.Metadata.Modified.Format("2006-01-02 15:04:05"))
    },
}

// 配置设置命令
var configSetCmd = &cobra.Command{
    Use:   "set <key> <value>",
    Short: "设置配置值",
    Args:  cobra.ExactArgs(2),
    Run: func(cmd *cobra.Command, args []string) {
        key := args[0]
        value := args[1]
        
        // 尝试推断类型
        var typedValue interface{} = value
        if intVal, err := strconv.Atoi(value); err == nil {
            typedValue = intVal
        } else if floatVal, err := strconv.ParseFloat(value, 64); err == nil {
            typedValue = floatVal
        } else if boolVal, err := strconv.ParseBool(value); err == nil {
            typedValue = boolVal
        }
        
        if err := SetNestedValue(key, typedValue); err != nil {
            fmt.Printf("❌ 设置值失败: %v\n", err)
            return
        }
        
        fmt.Printf("🔧 配置更新成功\n")
        fmt.Printf("键: %s\n", key)
        fmt.Printf("值: %v\n", typedValue)
        fmt.Printf("类型: %T\n", typedValue)
        fmt.Printf("格式: %s\n", config.Format)
    },
}
```

请记得在`init()`函数中注册所有中间件，并在整个应用程序中实现适当的错误处理！