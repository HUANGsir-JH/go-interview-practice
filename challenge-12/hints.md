# 挑战12提示：带有高级错误处理的文件处理流水线

## 提示1：自定义错误类型的实现
创建提供上下文信息并实现 error 接口的错误类型：
```go
type ValidationError struct {
    Field   string
    Message string
    Err     error
}

func (e *ValidationError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("字段 '%s' 验证失败: %s: %v", e.Field, e.Message, e.Err)
    }
    return fmt.Sprintf("字段 '%s' 验证失败: %s", e.Field, e.Message)
}

func (e *ValidationError) Unwrap() error {
    return e.Err
}
```

## 提示2：错误包装与上下文
使用 fmt.Errorf 中的 %w 来包装错误，保留错误链：
```go
func (p *Pipeline) Process(ctx context.Context) error {
    // 读取阶段
    data, err := p.Reader.Read(ctx)
    if err != nil {
        return &PipelineError{
            Stage: "read",
            Err:   fmt.Errorf("读取数据失败: %w", err),
        }
    }
    
    // 验证阶段
    for i, validator := range p.Validators {
        if err := validator.Validate(data); err != nil {
            return &PipelineError{
                Stage: fmt.Sprintf("validation_%d", i),
                Err:   fmt.Errorf("验证步骤 %d 失败: %w", i, err),
            }
        }
    }
}
```

## 提示3：哨兵错误的创建与使用
为常见情况定义包级别的哨兵错误：
```go
var (
    ErrInvalidFormat    = errors.New("数据格式无效")
    ErrMissingField     = errors.New("缺少必填字段")
    ErrProcessingFailed = errors.New("处理失败")
    ErrDestinationFull  = errors.New("目标位置已满")
)

// 在验证器中的使用
func (v *JSONValidator) Validate(data []byte) error {
    if !json.Valid(data) {
        return fmt.Errorf("数据不是有效的 JSON: %w", ErrInvalidFormat)
    }
    return nil
}
```

## 提示4：基于类型的错误处理与 errors.As
使用 errors.As 检查特定错误类型：
```go
func handlePipelineError(err error) {
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        log.Printf("字段 '%s' 出现验证错误: %s", validationErr.Field, validationErr.Message)
        return
    }
    
    var transformErr *TransformError
    if errors.As(err, &transformErr) {
        log.Printf("转换阶段 '%s' 出错: %v", transformErr.Stage, transformErr.Err)
        return
    }
    
    // 检查哨兵错误
    if errors.Is(err, ErrInvalidFormat) {
        log.Println("检测到格式无效")
        return
    }
}
```

## 提示5：流水线结构与流程
实现流水线以通过所有阶段处理数据：
```go
type Pipeline struct {
    Reader       Reader
    Validators   []Validator
    Transformers []Transformer
    Writer       Writer
}

func (p *Pipeline) Process(ctx context.Context) error {
    // 阶段1：读取
    data, err := p.Reader.Read(ctx)
    if err != nil {
        return &PipelineError{Stage: "read", Err: err}
    }
    
    // 阶段2：验证
    for i, validator := range p.Validators {
        if err := validator.Validate(data); err != nil {
            return &PipelineError{
                Stage: fmt.Sprintf("validate_%d", i),
                Err:   err,
            }
        }
    }
    
    // 阶段3：转换
    for i, transformer := range p.Transformers {
        data, err = transformer.Transform(data)
        if err != nil {
            return &PipelineError{
                Stage: fmt.Sprintf("transform_%d", i),
                Err:   err,
            }
        }
    }
    
    // 阶段4：写入
    if err := p.Writer.Write(ctx, data); err != nil {
        return &PipelineError{Stage: "write", Err: err}
    }
    
    return nil
}
```

## 提示6：并发错误处理
正确处理多个 goroutine 的错误：
```go
func (p *Pipeline) handleErrors(ctx context.Context, errs <-chan error) error {
    select {
    case err := <-errs:
        if err != nil {
            return fmt.Errorf("并发操作失败: %w", err)
        }
        return nil
    case <-ctx.Done():
        return fmt.Errorf("操作被取消: %w", ctx.Err())
    }
}

// 并发处理并收集错误的示例
func (p *Pipeline) ProcessConcurrently(ctx context.Context, inputs [][]byte) error {
    errChan := make(chan error, len(inputs))
    
    for _, input := range inputs {
        go func(data []byte) {
            if err := p.processOne(ctx, data); err != nil {
                errChan <- err
                return
            }
            errChan <- nil
        }(input)
    }
    
    // 收集错误
    for i := 0; i < len(inputs); i++ {
        if err := <-errChan; err != nil {
            return err
        }
    }
    
    return nil
}
```

## 提示7：带错误处理的资源清理
即使发生错误也要实现正确的清理：
```go
func (p *Pipeline) ProcessWithCleanup(ctx context.Context) (retErr error) {
    // 设置资源
    if setupErr := p.setup(); setupErr != nil {
        return fmt.Errorf("设置失败: %w", setupErr)
    }
    
    // 延迟清理 - 即使因错误提前返回也会执行
    defer func() {
        if cleanupErr := p.cleanup(); cleanupErr != nil {
            if retErr != nil {
                // 处理和清理均失败
                retErr = fmt.Errorf("处理失败: %w, 清理也失败: %v", retErr, cleanupErr)
            } else {
                // 仅清理失败
                retErr = fmt.Errorf("清理失败: %w", cleanupErr)
            }
        }
    }()
    
    // 主要处理逻辑
    return p.Process(ctx)
}
```

## 关键错误处理概念：
- **自定义错误类型**：提供上下文信息并实现 Unwrap()
- **错误包装**：使用 %w 保留错误链
- **哨兵错误**：为常见条件定义包级别错误
- **errors.Is**：检查错误是否为或包裹某个哨兵错误
- **errors.As**：从错误链中提取特定错误类型
- **上下文保留**：始终提供错误发生位置的上下文
- **资源清理**：使用 defer 确保即使出错也能执行清理