# 贪心算法硬币找零学习资料

## 理解贪心算法

贪心算法是一种简单但强大的优化问题求解方法。它在每一步都做出局部最优的选择，希望这些选择能导致全局最优解。虽然贪心算法并不总是能为所有问题提供最优解，但它们效率高，通常能给出良好的近似解。

### 贪心算法的工作原理

贪心算法的一般过程如下：

1. 在每一步选择局部最优解
2. 永不重新考虑之前的决策
3. 一直进行直到获得完整解

### 贪心算法的特点

- **贪心选择性质**：通过做出局部最优选择，可以达到全局最优解。
- **最优子结构**：问题的最优解包含其子问题的最优解。
- **简洁性**：贪心算法通常比其他方法更容易实现和理解。
- **高效性**：贪心算法通常比动态规划或暴力法更高效。

## 硬币找零问题

硬币找零问题问的是：给定一组硬币面额和一个目标金额，最少需要多少枚硬币才能凑成该金额？

### 贪心法解决硬币找零

贪心法解决硬币找零问题的步骤如下：

1. 将面额按降序排序
2. 从最大面额开始
3. 尽可能多地取当前面额的硬币，但不超过目标金额
4. 转到下一个最大的面额
5. 重复直到达到目标金额或用完所有面额

以下是 Go 语言的简单实现：

```go
func minCoins(amount int, denominations []int) int {
    // 将面额按降序排序
    sort.Sort(sort.Reverse(sort.IntSlice(denominations)))
    
    coinCount := 0
    remainingAmount := amount
    
    for _, coin := range denominations {
        // 尽可能多地取当前面额的硬币
        count := remainingAmount / coin
        coinCount += count
        remainingAmount -= count * coin
        
        // 如果已达到目标金额，则完成
        if remainingAmount == 0 {
            return coinCount
        }
    }
    
    // 如果无法凑出精确金额
    if remainingAmount > 0 {
        return -1
    }
    
    return coinCount
}
```

### 找到具体的硬币组合

为了找出具体的硬币组合，我们修改算法以记录每种面额使用的数量：

```go
func coinCombination(amount int, denominations []int) map[int]int {
    // 将面额按降序排序
    sort.Sort(sort.Reverse(sort.IntSlice(denominations)))
    
    combination := make(map[int]int)
    remainingAmount := amount
    
    for _, coin := range denominations {
        // 尽可能多地取当前面额的硬币
        count := remainingAmount / coin
        if count > 0 {
            combination[coin] = count
        }
        remainingAmount -= count * coin
        
        // 如果已达到目标金额，则完成
        if remainingAmount == 0 {
            return combination
        }
    }
    
    // 如果无法凑出精确金额，返回空映射
    if remainingAmount > 0 {
        return map[int]int{}
    }
    
    return combination
}
```

## 贪心算法适用的情况（以及不适用的情况）

贪心法在标准美国硬币面额（1、5、10、25、50、100）下能产生最优解，但对于所有面额集合并不总是能得到最优结果。

### 贪心法有效的例子

使用美国面额 [1, 5, 10, 25, 50]：
- 要凑出 42 美分时，贪心法的结果是：
  - 1 枚 25 美分 + 1 枚 10 美分 + 1 枚 5 美分 + 2 枚 1 美分 = 5 枚硬币
  - 这确实是最佳方案

### 贪心法失败的例子

使用面额 [1, 3, 4]：
- 要凑出 6 美分时，贪心法的结果是：
  - 1 枚 4 美分 + 2 枚 1 美分 = 3 枚硬币
  - 但最优解是 2 枚硬币：2 枚 3 美分 = 6 美分

## 贪心算法何时适用于硬币找零？

当硬币系统具有**规范性质**时，贪心算法能提供最优解。一个硬币系统具有这种性质，如果每个硬币都可以用较小面额的硬币最优表示。

美国硬币系统（1、5、10、25、50、100）具有这一性质，因此贪心法在此系统中有效。

## 动态规划替代方案

对于贪心法不能始终产生最优解的硬币系统，动态规划是一种更可靠的解决方案：

```go
func minCoinsDP(amount int, denominations []int) int {
    // 初始化 dp 数组，值为 amount+1（大于可能的最大硬币数）
    dp := make([]int, amount+1)
    for i := range dp {
        dp[i] = amount + 1
    }
    dp[0] = 0 // 基础情况：凑出 0 金额需要 0 枚硬币
    
    // 构建 dp 数组
    for _, coin := range denominations {
        for i := coin; i <= amount; i++ {
            if dp[i-coin]+1 < dp[i] {
                dp[i] = dp[i-coin] + 1
            }
        }
    }
    
    // 如果 dp[amount] 仍为 amount+1，则无法凑出该金额
    if dp[amount] > amount {
        return -1
    }
    return dp[amount]
}
```

## 处理边界情况

在实现硬币找零算法时，需要注意以下边界情况：

1. **金额为零**：返回 0（无需硬币）
2. **负金额**：返回 -1 或抛出错误
3. **无法凑出精确金额**：返回 -1 或返回无法实现的标志
4. **面额数组为空**：返回 -1 或抛出错误

## 性能考虑

- **时间复杂度**：
  - 贪心法：O(n log n) 用于排序 + O(n) 用于找硬币 = O(n log n)
  - 动态规划法：O(n × amount)，其中 n 是面额数量
  
- **空间复杂度**：
  - 贪心法：O(n) 用于存储结果
  - 动态规划法：O(amount) 用于 dp 数组

## 进一步阅读

1. [贪心算法（GeeksforGeeks）](https://www.geeksforgeeks.org/greedy-algorithms/)
2. [硬币找零问题（GeeksforGeeks）](https://www.geeksforgeeks.org/coin-change-dp-7/)
3. [贪心算法在硬币找零中何时有效？](https://graal.ift.ulaval.ca/~dadub100/ChapIV/node14.html)
4. [动态规划 vs 贪心法](https://www.geeksforgeeks.org/dynamic-programming-vs-greedy-approach/)