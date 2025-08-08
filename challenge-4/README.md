[查看排行榜](SCOREBOARD.md)

# 挑战 4：并发图BFS查询

您需要在单个图上并发处理多个广度优先搜索（BFS）查询。每个查询指定一个起始节点，您必须计算从该节点开始的BFS顺序。与简单的单线程BFS不同，您的解决方案应该利用goroutine和通道（或并发安全的数据结构）来高效地并行处理多个查询。

## 函数签名

```go
func ConcurrentBFSQueries(graph map[int][]int, queries []int, numWorkers int) map[int][]int
```

参数：
- graph：图的邻接表表示。
  - 键是节点（整数）。
  - 值是相邻节点的切片。
- queries：需要执行BFS的起始节点切片。
- numWorkers：并发处理这些BFS查询的goroutine（工作器）数量。

返回：
- 从查询节点到从该节点开始的BFS顺序的映射。

## 要求

1. 您必须使用并发（goroutine + 通道，或并发安全的数据结构）来并行处理BFS查询。
2. 朴素或纯顺序的方法可能太慢，特别是对于大型图和许多查询。
3. BFS算法本身可以是标准的（使用队列），但如果工作器可用，每个BFS查询应该并发运行。

## 示例用法（官方测试不测试）

```go
func main() {
    graph := map[int][]int{
        0: {1, 2},
        1: {2, 3},
        2: {3},
        3: {4},
        4: {},
    }
    queries := []int{0, 1, 2}
    numWorkers := 2

    results := ConcurrentBFSQueries(graph, queries, numWorkers)
    /*
       可能的输出：
       results[0] = [0 1 2 3 4]
       results[1] = [1 2 3 4]
       results[2] = [2 3 4]
    */
}
```

## 操作说明

1. Fork 这个仓库并 clone 您的 fork。
2. 为您的提交创建目录：`challenge-4/submissions/<您的github用户名>/`。
3. 将 `solution-template.go` 复制到您的提交目录中。
4. 实现函数 `ConcurrentBFSQueries(graph map[int][]int, queries []int, numWorkers int) map[int][]int`。
5. 使用 goroutine 并行处理BFS查询，尊重工作器数量。
6. 用您的解决方案打开拉取请求。

## 本地测试

在 `challenge-4/` 目录内运行：

```bash
go test -v
```