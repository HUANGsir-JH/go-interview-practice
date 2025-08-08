# 并发图BFS查询提示

## 提示 1：工作池模式
你需要实现一个工作池模式。创建 `numWorkers` 个 goroutine，从通道中处理 BFS 查询：
```go
jobs := make(chan int, len(queries))
results := make(chan BFSResult, len(queries))
```

## 提示 2：BFS结果结构
定义一个结构体来存储BFS结果：
```go
type BFSResult struct {
    StartNode int
    Order     []int
}
```

## 提示 3：启动工作goroutine
启动指定数量的工作goroutine：
```go
for i := 0; i < numWorkers; i++ {
    go worker(graph, jobs, results)
}
```

## 提示 4：发送任务
将所有查询发送到 jobs 通道并关闭它：
```go
for _, query := range queries {
    jobs <- query
}
close(jobs)
```

## 提示 5：标准BFS实现
每个工作goroutine使用队列执行标准BFS：
```go
func bfs(graph map[int][]int, start int) []int {
    visited := make(map[int]bool)
    queue := []int{start}
    order := []int{}
    // ... 实现BFS
}
```

## 提示 6：工作函数结构
工作函数应持续处理任务直到通道被关闭：
```go
func worker(graph map[int][]int, jobs <-chan int, results chan<- BFSResult) {
    for start := range jobs {
        order := bfs(graph, start)
        results <- BFSResult{StartNode: start, Order: order}
    }
}
```

## 提示 7：收集结果
收集所有结果并转换为所需的map格式：
```go
resultMap := make(map[int][]int)
for i := 0; i < len(queries); i++ {
    result := <-results
    resultMap[result.StartNode] = result.Order
}
```

## 提示 8：BFS队列操作
对于BFS，使用切片操作实现队列：
```go
// 出队（从前面移除）
node := queue[0]
queue = queue[1:]

// 入队（添加到末尾）
queue = append(queue, neighbor)
```