[查看排行榜](SCOREBOARD.md)

# 挑战 11：并发网页内容聚合器

## 问题描述

实现一个并发网页内容聚合器，能够从多个来源并发地获取、处理和聚合数据，并具备适当的并发控制和上下文处理能力。

## 要求

1. 实现一个 `ContentAggregator`，要求：
   - 并发地从多个 URL 获取内容
   - 处理内容（提取特定信息）
   - 聚合结果并具备完善的错误处理机制
   - 使用正确的上下文管理来支持取消和超时
   - 实现请求速率限制，避免对源服务器造成过载

2. 必须实现以下并发模式：
   - **工作池**：使用固定数量的工作 goroutine 来处理获取的内容
   - **扇出、扇入**：分发处理任务并收集结果
   - **上下文处理**：正确传播取消和超时信号
   - **速率限制**：使用令牌桶或其他类似方法限制请求速率
   - **并发数据结构**：安全访问共享数据

3. 解决方案应体现对以下内容的理解：
   - goroutine 和 channel 管理
   - 并发代码中的正确错误处理
   - 同步原语（Mutex、RWMutex、WaitGroup）
   - 使用 context 包管理请求生命周期
   - 优雅关闭

## 函数签名

```go
// 核心类型
type ContentFetcher interface {
    Fetch(ctx context.Context, url string) ([]byte, error)
}

type ContentProcessor interface {
    Process(ctx context.Context, content []byte) (ProcessedData, error)
}

type ProcessedData struct {
    Title       string
    Description string
    Keywords    []string
    Timestamp   time.Time
    Source      string
}

type ContentAggregator struct {
    // 根据需要添加字段
}

// 构造函数
func NewContentAggregator(
    fetcher ContentFetcher, 
    processor ContentProcessor, 
    workerCount int, 
    requestsPerSecond int,
) *ContentAggregator

// 方法
func (ca *ContentAggregator) FetchAndProcess(
    ctx context.Context, 
    urls []string,
) ([]ProcessedData, error)

func (ca *ContentAggregator) Shutdown() error

// 不同并发模式的辅助函数
func (ca *ContentAggregator) workerPool(
    ctx context.Context, 
    jobs <-chan string, 
    results chan<- ProcessedData,
    errors chan<- error,
)

func (ca *ContentAggregator) fanOut(
    ctx context.Context, 
    urls []string,
) ([]ProcessedData, []error)
```

## 约束条件

- 解决方案必须能优雅处理错误，且绝不丢失错误信息
- 实现正确的资源清理（关闭 channel、释放锁等）
- 并发请求数量应可配置
- 必须实现请求速率限制
- 超时和取消必须得到妥善处理
- 代码应防止 goroutine 泄漏

## 示例用法

```go
// 创建内容获取器和处理器
fetcher := &HTTPFetcher{
    Client: &http.Client{Timeout: 5 * time.Second},
}
processor := &HTMLProcessor{}

// 创建聚合器，设置 5 个工作线程，每秒最多 10 个请求
aggregator := NewContentAggregator(fetcher, processor, 5, 10)

// 带超时的上下文
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

// 需要获取和处理的 URL 列表
urls := []string{
    "https://example.com",
    "https://example.org",
    "https://example.net",
    // 根据需要添加更多 URL
}

// 并行获取和处理，同时进行速率限制
results, err := aggregator.FetchAndProcess(ctx, urls)
if err != nil {
    log.Fatalf("聚合操作出错: %v", err)
}

// 处理结果
for _, data := range results {
    fmt.Printf("标题: %s\n来源: %s\n关键词: %v\n\n", 
        data.Title, data.Source, data.Keywords)
}

// 清理资源
aggregator.Shutdown()
```

## 指令

- **Fork** 该仓库。
- **Clone** 你的 fork 到本地机器。
- 在 `challenge-11/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的接口和类型。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 你的代码到你的 fork。
- **创建** 一个 pull request 提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-11/` 目录下运行以下命令：

```bash
go test -v
```