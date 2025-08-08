# 挑战 30：上下文管理实现

## 概述

实现一个上下文管理器，展示 Go `context` 包的核心模式。`context` 包是管理取消信号、超时和请求范围值的基础，在 Go 应用程序中至关重要。

## 你的任务

实现一个 `ContextManager` 接口，包含 **6 个核心方法** 和 **2 个辅助函数**：

### ContextManager 接口

```go
type ContextManager interface {
    // 从父上下文中创建可取消的上下文
    CreateCancellableContext(parent context.Context) (context.Context, context.CancelFunc)
    
    // 创建带有超时的上下文
    CreateTimeoutContext(parent context.Context, timeout time.Duration) (context.Context, context.CancelFunc)
    
    // 向上下文中添加值
    AddValue(parent context.Context, key, value interface{}) context.Context
    
    // 从上下文中获取值
    GetValue(ctx context.Context, key interface{}) (interface{}, bool)
    
    // 使用上下文取消支持执行任务
    ExecuteWithContext(ctx context.Context, task func() error) error
    
    // 等待一段时间或直到上下文被取消
    WaitForCompletion(ctx context.Context, duration time.Duration) error
}
```

### 辅助函数

```go
// 模拟可被取消的工作
func SimulateWork(ctx context.Context, workDuration time.Duration, description string) error

// 具有上下文感知能力地处理多个项目
func ProcessItems(ctx context.Context, items []string) ([]string, error)
```

## 要求

### 核心功能
1. **上下文取消**：通过 `context.WithCancel` 处理手动取消
2. **上下文超时**：通过 `context.WithTimeout` 实现超时行为
3. **值存储**：通过 `context.WithValue` 存储和检索值
4. **任务执行**：支持取消的函数执行
5. **等待操作**：在尊重取消的前提下等待指定时长

### 实现细节

- 使用 Go 标准库中的 `context` 包函数
- 正确处理 `context.Canceled` 和 `context.DeadlineExceeded` 错误
- 返回适当的布尔标志以表示值是否存在
- 支持基于 goroutine 的任务执行，并进行适当的同步
- 分批处理项目，并在每个项目之间检查取消状态

## 测试覆盖率

你的实现将通过 **13 个测试用例** 进行测试，涵盖：

- 上下文创建与取消
- 超时行为
- 值的存储与检索
- 任务执行场景（成功、错误、取消）
- 等待操作（完成与取消）
- 辅助函数行为
- 集成场景

## 开始准备

1. 查看解决方案模板和测试文件
2. 从简单的 `AddValue` 和 `GetValue` 方法开始
3. 逐步实现取消和超时上下文
4. 实现带有适当 goroutine 处理的任务执行
5. 频繁运行测试，使用 `go test -v`

**提示**：查看 `learning.md` 文件以获取完整的上下文模式和示例！