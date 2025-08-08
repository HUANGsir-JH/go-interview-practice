[查看排行榜](SCOREBOARD.md)

# 挑战 25：图算法 - 最短路径

## 问题描述

实现多种图的最短路径算法，以在不同类型的图中找到顶点之间的最短路径。本挑战将测试你对图论和路径查找算法的理解。

你需要实现三种不同的最短路径算法：

1. `BreadthFirstSearch` - 用于无权图，从源顶点到所有其他顶点找到最短路径。
2. `Dijkstra` - 用于具有非负权重的加权图，从源顶点到所有其他顶点找到最短路径。
3. `BellmanFord` - 用于可能包含负权边的加权图，从源顶点到所有其他顶点找到最短路径，并检测负权环。

## 函数签名

```go
func BreadthFirstSearch(graph [][]int, source int) ([]int, []int)
func Dijkstra(graph [][]int, weights [][]int, source int) ([]int, []int)
func BellmanFord(graph [][]int, weights [][]int, source int) ([]int, []bool, []int)
```

## 输入格式

- `graph` - 一个二维邻接表，其中 `graph[i]` 是从顶点 `i` 出发有边连接的顶点列表。
- `weights` - 一个二维邻接表，其中 `weights[i][j]` 是从顶点 `i` 到 `graph[i][j]` 的边的权重。
- `source` - 用于寻找最短路径的源顶点。

## 输出格式

- `BreadthFirstSearch` 返回：
  - 一个距离切片，其中 `distances[i]` 表示从源点到顶点 `i` 的最短距离。
  - 一个前驱切片，其中 `predecessors[i]` 表示从源点到顶点 `i` 的最短路径中顶点 `i` 的前一个顶点。

- `Dijkstra` 返回：
  - 一个距离切片，其中 `distances[i]` 表示从源点到顶点 `i` 的最短距离。
  - 一个前驱切片，其中 `predecessors[i]` 表示从源点到顶点 `i` 的最短路径中顶点 `i` 的前一个顶点。

- `BellmanFord` 返回：
  - 一个距离切片，其中 `distances[i]` 表示从源点到顶点 `i` 的最短距离。
  - 一个布尔值切片，其中 `hasPath[i]` 为 true 表示存在一条从源点到顶点 `i` 且不经过负权环的路径，否则为 false。
  - 一个前驱切片，其中 `predecessors[i]` 表示从源点到顶点 `i` 的最短路径中顶点 `i` 的前一个顶点。

## 要求

1. `BreadthFirstSearch` 应实现用于无权图的广度优先搜索算法。
2. `Dijkstra` 应实现用于具有非负权重的加权图的 Dijkstra 算法。
3. `BellmanFord` 应实现用于可能包含负权边的加权图的 Bellman-Ford 算法，并能检测负权环。
4. 所有算法都应正确处理边界情况，包括孤立顶点和不连通图。
5. 如果某个顶点无法从源点到达，其距离应设为无穷大（在 Go 中表示为 `int(1e9)` 或 `math.MaxInt32`）。
6. 如果某个顶点是源点，其距离应为 0，前驱应为 -1。

## 示例输入与输出

### 示例输入 1 (BFS)

```go
graph := [][]int{
    {1, 2},    // 顶点 0 有边连接到顶点 1 和 2
    {0, 3, 4}, // 顶点 1 有边连接到顶点 0、3 和 4
    {0, 5},    // 顶点 2 有边连接到顶点 0 和 5
    {1},       // 顶点 3 有边连接到顶点 1
    {1},       // 顶点 4 有边连接到顶点 1
    {2},       // 顶点 5 有边连接到顶点 2
}
source := 0
```

### 示例输出 1 (BFS)

```go
distances := []int{0, 1, 1, 2, 2, 2}
predecessors := []int{-1, 0, 0, 1, 1, 2}
```

### 示例输入 2 (Dijkstra)

```go
graph := [][]int{
    {1, 2},    // 顶点 0 有边连接到顶点 1 和 2
    {0, 3, 4}, // 顶点 1 有边连接到顶点 0、3 和 4
    {0, 5},    // 顶点 2 有边连接到顶点 0 和 5
    {1},       // 顶点 3 有边连接到顶点 1
    {1},       // 顶点 4 有边连接到顶点 1
    {2},       // 顶点 5 有边连接到顶点 2
}
weights := [][]int{
    {5, 10},   // 从 0 到 1 的边权重为 5，从 0 到 2 的边权重为 10
    {5, 3, 2}, // 从顶点 1 出发的边权重
    {10, 2},   // 从顶点 2 出发的边权重
    {3},       // 从顶点 3 出发的边权重
    {2},       // 从顶点 4 出发的边权重
    {2},       // 从顶点 5 出发的边权重
}
source := 0
```

### 示例输出 2 (Dijkstra)

```go
distances := []int{0, 5, 10, 8, 7, 12}
predecessors := []int{-1, 0, 0, 1, 1, 2}
```

### 示例输入 3 (Bellman-Ford)

```go
graph := [][]int{
    {1, 2},
    {3},
    {1, 3},
    {4},
    {},
}
weights := [][]int{
    {6, 7},   // 从顶点 0 出发的边权重
    {5},      // 从顶点 1 出发的边权重
    {-2, 4},  // 从顶点 2 出发的边权重（注意负权重）
    {2},      // 从顶点 3 出发的边权重
    {},       // 从顶点 4 出发的边权重
}
source := 0
```

### 示例输出 3 (Bellman-Ford)

```go
distances := []int{0, 6, 7, 11, 13}
hasPath := []bool{true, true, true, true, true}
predecessors := []int{-1, 0, 0, 2, 3}
```

## 指令

- **Fork** 仓库。
- **Clone** 你的 fork 到本地机器。
- **创建** 一个以你的 GitHub 用户名命名的目录，放在 `challenge-25/submissions/` 下。
- **复制** `solution-template.go` 文件到你的提交目录。
- **实现** 所需函数。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的 fork。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-25/` 目录下运行以下命令：

```bash
go test -v
```

## 性能期望

- **BreadthFirstSearch**: 时间复杂度 O(V + E)，其中 V 是顶点数，E 是边数。
- **Dijkstra**: 使用优先队列时时间复杂度为 O((V + E) log V)。
- **BellmanFord**: 时间复杂度为 O(V * E)。