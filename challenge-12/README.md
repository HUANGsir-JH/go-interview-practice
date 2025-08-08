[查看排行榜](SCOREBOARD.md)

# 挑战 12：带有高级错误处理的文件处理流水线

## 问题描述

实现一个文件处理流水线，能够读取、转换和写入数据，并具备全面的错误处理机制，展示 Go 语言在错误处理方面的惯用方式。

## 要求

1. 实现一个模块化的文件处理流水线，要求：
   - 从多种来源（文件、网络、内存）读取数据
   - 通过多个处理阶段对数据进行验证和转换
   - 将结果写入目标位置
   - 在每个阶段都实现全面的错误处理

2. 必须实现以下错误处理技术：
   - 嵌入标准错误的自定义错误类型
   - 错误包装以保留跨流水线阶段的上下文
   - 用于特定条件的哨兵错误
   - 使用 `errors.Is` 和 `errors.As` 的基于类型的错误处理
   - 在并发环境中正确传播错误

3. 流水线应包含以下组件：
   - **读取器**：从源（文件、URL、内存）读取数据
   - **验证器**：根据规则验证数据
   - **转换器**：将有效数据转换为不同格式
   - **写入器**：将处理后的数据写入目标
   - **流水线**：协调各组件之间的流程

## 函数签名

```go
// 核心接口
type Reader interface {
    Read(ctx context.Context) ([]byte, error)
}

type Validator interface {
    Validate(data []byte) error
}

type Transformer interface {
    Transform(data []byte) ([]byte, error)
}

type Writer interface {
    Write(ctx context.Context, data []byte) error
}

// 自定义错误类型
type ValidationError struct {
    Field   string
    Message string
    Err     error
}

type TransformError struct {
    Stage string
    Err   error
}

type PipelineError struct {
    Stage string
    Err   error
}

// 错误方法
func (e *ValidationError) Error() string
func (e *ValidationError) Unwrap() error

func (e *TransformError) Error() string
func (e *TransformError) Unwrap() error

func (e *PipelineError) Error() string
func (e *PipelineError) Unwrap() error

// 哨兵错误
var (
    ErrInvalidFormat    = errors.New("数据格式无效")
    ErrMissingField     = errors.New("必需字段缺失")
    ErrProcessingFailed = errors.New("处理失败")
    ErrDestinationFull  = errors.New("目标已满")
)

// 流水线实现
type Pipeline struct {
    Reader      Reader
    Validators  []Validator
    Transformers []Transformer
    Writer      Writer
}

func NewPipeline(r Reader, v []Validator, t []Transformer, w Writer) *Pipeline

func (p *Pipeline) Process(ctx context.Context) error

// 用于并发操作中处理错误的辅助函数
func (p *Pipeline) handleErrors(ctx context.Context, errs <-chan error) error
```

## 约束条件

- 所有错误必须提供关于出错位置和原因的有意义上下文
- 在适当情况下使用 `%w` 进行错误包装以维护错误链
- 使用 `errors.Is` 和 `errors.As` 实现正确的错误比较
- 展示哨兵错误检查和基于类型的错误处理
- 在并发操作中实现优雅的错误处理
- 当流水线失败时，应正确清理资源

## 示例用法

```go
// 创建流水线组件
fileReader := NewFileReader("input.json")
validators := []Validator{
    NewJSONValidator(),
    NewSchemaValidator(schema),
}
transformers := []Transformer{
    NewFieldTransformer("date", dateFormatter),
    NewDataEnricher(enrichmentService),
}
fileWriter := NewFileWriter("output.json")

// 创建并运行流水线
pipeline := NewPipeline(fileReader, validators, transformers, fileWriter)

// 使用上下文支持取消
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

err := pipeline.Process(ctx)
if err != nil {
    // 检查特定错误类型
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        fmt.Printf("字段 '%s' 验证失败: %s\n", validationErr.Field, validationErr.Message)
    } else if errors.Is(err, ErrInvalidFormat) {
        fmt.Println("文件格式无效")
    } else {
        fmt.Printf("流水线失败: %v\n", err)
    }
    
    // 打印完整的错误链
    fmt.Printf("错误链: %+v\n", err)
}
```

## 指令

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- **创建** 一个以你的 GitHub 用户名命名的目录，位于 `challenge-12/submissions/` 内。
- **复制** `solution-template.go` 文件到你的提交目录中。
- **实现** 所需的接口和错误类型。
- **本地测试** 你的解决方案，运行测试文件。
- **提交** 并 **推送** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-12/` 目录中运行以下命令：

```bash
go test -v
```