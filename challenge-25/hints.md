# 挑战25提示：图算法 - 最短路径

## 提示1：无权图的BFS - 初始化设置
使用队列和距离追踪来设置BFS：
```go
func BreadthFirstSearch(graph [][]int, source int) ([]int, []int) {
    n := len(graph)
    distances := make([]int, n)
    predecessors := make([]int, n)
    visited := make([]bool, n)
    
    // 将距离初始化为无穷大
    for i := range distances {
        distances[i] = 1e9
        predecessors[i] = -1
    }
    
    distances[source] = 0
    
    // BFS队列实现
    queue := []int{source}
    visited[source] = true
    
    for len(queue) > 0 {
        current := queue[0]
        queue = queue[1:]
        
        for _, neighbor := range graph[current] {
            if !visited[neighbor] {
                visited[neighbor] = true
                distances[neighbor] = distances[current] + 1
                predecessors[neighbor] = current
                queue = append(queue, neighbor)
            }
        }
    }
    
    return distances, predecessors
}
```

## 提示2：Dijkstra算法 - 优先队列
使用优先队列始终优先处理距离最近的顶点：
```go
import "container/heap"

type PriorityQueue []Node

type Node struct {
    vertex   int
    distance int
}

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].distance < pq[j].distance }
func (pq PriorityQueue) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
    *pq = append(*pq, x.(Node))
}

func (pq *PriorityQueue) Pop() interface{} {
    old := *pq
    n := len(old)
    node := old[n-1]
    *pq = old[0 : n-1]
    return node
}
```

## 提示3：Dijkstra算法实现
实现主要的Dijkstra算法：
```go
func Dijkstra(graph [][]int, weights [][]int, source int) ([]int, []int) {
    n := len(graph)
    distances := make([]int, n)
    predecessors := make([]int, n)
    visited := make([]bool, n)
    
    for i := range distances {
        distances[i] = 1e9
        predecessors[i] = -1
    }
    
    distances[source] = 0
    
    pq := &PriorityQueue{}
    heap.Init(pq)
    heap.Push(pq, Node{vertex: source, distance: 0})
    
    for pq.Len() > 0 {
        current := heap.Pop(pq).(Node)
        vertex := current.vertex
        
        if visited[vertex] {
            continue
        }
        visited[vertex] = true
        
        for i, neighbor := range graph[vertex] {
            weight := weights[vertex][i]
            newDistance := distances[vertex] + weight
            
            if newDistance < distances[neighbor] {
                distances[neighbor] = newDistance
                predecessors[neighbor] = vertex
                heap.Push(pq, Node{vertex: neighbor, distance: newDistance})
            }
        }
    }
    
    return distances, predecessors
}
```

## 提示4：Bellman-Ford初始化与边松弛
实现V-1次迭代的边松弛：
```go
func BellmanFord(graph [][]int, weights [][]int, source int) ([]int, []bool, []int) {
    n := len(graph)
    distances := make([]int, n)
    predecessors := make([]int, n)
    hasPath := make([]bool, n)
    
    for i := range distances {
        distances[i] = 1e9
        predecessors[i] = -1
        hasPath[i] = false
    }
    
    distances[source] = 0
    hasPath[source] = true
    
    // 松弛边 V-1 次
    for i := 0; i < n-1; i++ {
        for u := 0; u < n; u++ {
            if distances[u] == 1e9 {
                continue
            }
            
            for j, v := range graph[u] {
                weight := weights[u][j]
                if distances[u]+weight < distances[v] {
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
                    hasPath[v] = true
                }
            }
        }
    }
    
    // 检查负权环...
    return distances, hasPath, predecessors
}
```

## 关键图算法概念：
- **BFS**：按层级遍历，用于无权图的最短路径
- **Dijkstra**：使用优先队列的贪心算法，适用于非负权重
- **Bellman-Ford**：动态规划方法，可处理负权重
- **边松弛**：更新最短距离的核心操作
- **优先队列**：高效选择距离最小的顶点
- **负权环检测**：确保Bellman-Ford正确性的关键