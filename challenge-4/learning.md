# 并发图BFS查询学习材料

## Go中的并发与goroutine

Go从设计之初就将并发作为核心特性，使得编写高效利用多CPU核心和处理异步任务的程序变得非常容易。本挑战聚焦于实现图遍历中的并发广度优先搜索（BFS）。

### Goroutines

Goroutines是由Go运行时管理的轻量级线程。它们允许你以极小的开销并行运行函数：

```go
// 基本的goroutine
go functionName()  // 在独立的goroutine中运行函数

// 匿名函数作为goroutine
go func() {
    // 在此处执行工作
    fmt.Println("在goroutine中运行")
}()
```

与传统线程相比，goroutines具有以下优势：
- 成本低得多（仅需几KB内存，而线程需要MB级别）
- 由Go的运行时调度器管理，而非操作系统
- 可在单台机器上扩展至数十万甚至数百万个

### Channels

Channels是goroutine之间通信的主要机制。它们提供了一种带有内置同步的发送和接收值的方式：

```go
// 创建一个channel
ch := make(chan int)  // 无缓冲channel
bufferedCh := make(chan string, 10)  // 容量为10的缓冲channel

// 发送值（如果channel已满则阻塞）
ch <- 42
bufferedCh <- "hello"

// 接收值（如果channel为空则阻塞）
value := <-ch
message := <-bufferedCh

// 完成后关闭channel（可选）
close(ch)

// 检查channel是否已关闭
value, ok := <-ch  // 如果channel已关闭，ok为false
```

### Channel模式

几种使用channels的有效常见模式：

#### 扇出 / 扇入

使用多个goroutine并行处理数据，然后合并结果：

```go
func fanOut(input []int) <-chan int {
    // 将工作分发给多个goroutine
    out := make(chan int)
    
    go func() {
        defer close(out)
        for _, n := range input {
            out <- process(n)
        }
    }()
    
    return out
}

func fanIn(channels ...<-chan int) <-chan int {
    // 合并来自多个channel的结果
    out := make(chan int)
    var wg sync.WaitGroup
    
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for n := range c {
                out <- n
            }
        }(ch)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}
```

#### 工作池

创建固定数量的工作线程，从队列中处理任务：

```go
func workerPool(numWorkers int, tasks <-chan Task, results chan<- Result) {
    var wg sync.WaitGroup
    
    // 启动工作线程
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for task := range tasks {
                results <- processTask(task)
            }
        }(i)
    }
    
    wg.Wait()
    close(results)
}
```

### sync包

`sync`包提供了同步原语：

```go
// WaitGroup：等待一组goroutine完成
var wg sync.WaitGroup
wg.Add(n)  // 添加n个需要等待的goroutine
wg.Done()  // 标记一个goroutine已完成
wg.Wait()  // 阻塞直到所有goroutine都完成

// Mutex：保护对共享数据的访问
var mu sync.Mutex
mu.Lock()
// 临界区（同一时间只有一个goroutine可以进入）
mu.Unlock()

// RWMutex：允许多个读取者或一个写入者
var rwMu sync.RWMutex
rwMu.RLock() // 读锁（允许多个）
// 读取共享数据
rwMu.RUnlock()

rwMu.Lock() // 写锁（独占）
// 修改共享数据
rwMu.Unlock()
```

### context包

`context`包有助于在并发操作中管理取消和超时：

```go
// 创建带取消功能的context
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // 完成后调用cancel

// 创建带超时的context
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 检查context是否已结束
select {
case <-ctx.Done():
    // context被取消或超时
    return ctx.Err()
case result := <-resultChan:
    return result
}
```

### 使用BFS进行图遍历

广度优先搜索在进入下一层之前会访问当前深度的所有顶点。关键概念包括：

- **基于队列的方法**：使用队列数据结构来跟踪待访问的节点
- **已访问节点追踪**：记录已访问节点以避免循环
- **逐层处理**：在进入下一层前处理完当前距离的所有节点

### 并发BFS注意事项

在实现并发BFS时，请考虑以下几点：

1. **goroutine协调**：使用goroutine池来处理每一层的节点
2. **通信模式**：使用channels在工作线程间通信
3. **同步机制**：使用sync.WaitGroup等待每层完成
4. **共享状态保护**：如果多个goroutine共享visited映射，需使用mutex保护
5. **工作分配**：如何将图遍历工作分配给多个goroutine
6. **结果聚合**：如何安全地收集多个goroutine的结果

### BFS的重要并发模式

- **工作池**：固定数量的工作线程处理BFS任务
- **层级同步**：确保所有同一层级的节点处理完毕后再进入下一层
- **共享状态管理**：保护多个goroutine之间的已访问节点映射
- **channel通信**：使用channel分发工作和收集结果

### 并发陷阱

常见的陷阱需避免：

1. **竞态条件**：始终使用mutex或channel保护共享数据
2. **死锁**：避免goroutine无限期等待彼此的情况
3. **goroutine泄漏**：确保当工作完成后goroutine能正常退出
4. **channel误用**：注意channel关闭问题——只有发送方应关闭channel

## 进一步阅读

- [Go并发模式](https://blog.golang.org/pipelines)
- [Effective Go：并发](https://golang.org/doc/effective_go#concurrency)
- [可视化Go中的并发](https://divan.dev/posts/go_concurrency_visualize/)
- [Context包](https://blog.golang.org/context)