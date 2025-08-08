# 贪心硬币找零提示

## 提示 1：贪心算法策略
从最大面额开始，尽可能多地使用，然后移向下一个较小的面额：
```go
func makeChange(amount int, denominations []int) map[int]int {
    result := make(map[int]int)
    
    // 将面额按降序排序
    sort.Slice(denominations, func(i, j int) bool {
        return denominations[i] > denominations[j]
    })
    
    // 使用贪心方法
    for _, denom := range denominations {
        if amount >= denom {
            count := amount / denom
            result[denom] = count
            amount -= count * denom
        }
    }
    
    return result
}
```

## 提示 2：面额排序
始终先将面额按降序排序：
```go
sort.Slice(denominations, func(i, j int) bool {
    return denominations[i] > denominations[j]
})
```

## 提示 3：计算硬币数量
使用整数除法来确定每种面额的硬币数量：
```go
count := amount / denom
if count > 0 {
    result[denom] = count
    amount -= count * denom
}
```

## 提示 4：处理无法实现的情况
检查是否能凑出精确金额：
```go
func canMakeChange(amount int, denominations []int) bool {
    // 在贪心算法之后，检查剩余金额是否为 0
    remaining := amount
    for _, denom := range sortedDenominations {
        remaining %= denom
    }
    return remaining == 0
}
```

## 提示 5：替代返回格式
如果需要返回硬币总数：
```go
func minCoins(amount int, denominations []int) int {
    totalCoins := 0
    for _, denom := range sortedDenominations {
        coins := amount / denom
        totalCoins += coins
        amount -= coins * denom
    }
    return totalCoins
}
```

## 提示 6：边界情况
处理特殊情况：
```go
if amount == 0 {
    return make(map[int]int) // 空结果
}

if len(denominations) == 0 {
    return nil // 无法找零
}
```