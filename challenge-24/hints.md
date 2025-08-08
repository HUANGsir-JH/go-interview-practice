# 挑战24提示：动态规划 - 最长递增子序列

## 提示1：理解DP状态
关键在于定义 `dp[i]` 的含义：
- `dp[i]` = 以索引 `i` 结尾的最长递增子序列的长度
- 每个单独元素都构成一个长度为1的子序列
- 基础情况：初始化所有 `dp[i] = 1`

```go
dp := make([]int, len(nums))
for i := range dp {
    dp[i] = 1  // 每个元素都是长度为1的子序列
}
```

## 提示2：DP转移逻辑
对于每个位置 `i`，检查所有之前的的位置 `j`：
- 如果 `nums[j] < nums[i]`，我们可以扩展以 `j` 结尾的子序列
- 更新：`dp[i] = max(dp[i], dp[j] + 1)`
- 时间复杂度：O(n²)，由于嵌套循环

```go
for i := 1; i < len(nums); i++ {
    for j := 0; j < i; j++ {
        if nums[j] < nums[i] {
            dp[i] = max(dp[i], dp[j] + 1)
        }
    }
}
```

## 提示3：使用二分查找的优化方法
O(n²) 方法可以通过使用“tails”数组优化到 O(n log n)：
- `tails[i]` 存储所有长度为 `i+1` 的子序列中最小的结尾元素
- 对于每个数字，使用二分查找确定其应放置的位置
- 这保持了 `tails` 始终有序的性质

```go
tails := []int{}
for _, num := range nums {
    pos := sort.SearchInts(tails, num)
    if pos == len(tails) {
        tails = append(tails, num)  // 扩展序列
    } else {
        tails[pos] = num  // 用更小的结尾元素替换
    }
}
```

## 提示4：重构实际序列
为了获取实际的LIS元素（而不仅仅是长度）：
- 使用 `parent` 数组记录序列中每个元素的前驱
- 在DP过程中，当更新 `dp[i]` 时，同时设置 `parent[i] = j`
- DP结束后，找到最长长度对应的位置并回溯

```go
parent := make([]int, len(nums))
// 在DP过程中：如果更新了dp[i]，则设置parent[i] = j

// 重构：从maxIndex开始，沿着parent指针回溯
current := maxIndex
for i := maxLength - 1; i >= 0; i-- {
    lis[i] = nums[current]
    current = parent[current]
}
```

## LIS核心概念：
- **动态规划**：通过最优子结构从较小的子问题构建解
- **二分查找**：利用有序数组高效查找插入位置（O(log n)）
- **tails数组**：维护每个可能LIS长度的最小尾部元素，实现优化
- **重构**：使用父指针构建实际序列，而不仅仅是计算长度