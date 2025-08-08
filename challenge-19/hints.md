# 第19关提示：切片操作

## 提示1：FindMax - 遍历切片
先处理空切片的情况，然后遍历找到最大值：
```go
func FindMax(numbers []int) int {
    if len(numbers) == 0 {
        return 0
    }
    
    max := numbers[0] // 用第一个元素初始化
    for _, num := range numbers[1:] {
        if num > max {
            max = num
        }
    }
    return max
}
```

## 提示2：RemoveDuplicates - 使用Map进行追踪
使用map来记录已见的值，同时保持顺序：
```go
func RemoveDuplicates(numbers []int) []int {
    seen := make(map[int]bool)
    result := make([]int, 0, len(numbers))
    
    for _, num := range numbers {
        if !seen[num] {
            seen[num] = true
            result = append(result, num)
        }
    }
    return result
}
```

## 提示3：ReverseSlice - 两种方法
你可以通过创建新切片或原地交换来实现反转：
```go
// 方法1：创建新切片
func ReverseSlice(slice []int) []int {
    result := make([]int, len(slice))
    for i, val := range slice {
        result[len(slice)-1-i] = val
    }
    return result
}

// 方法2：复制并原地反转
func ReverseSlice(slice []int) []int {
    result := make([]int, len(slice))
    copy(result, slice)
    
    for i, j := 0, len(result)-1; i < j; i, j = i+1, j-1 {
        result[i], result[j] = result[j], result[i]
    }
    return result
}
```

## 提示4：FilterEven - 使用取模运算符
使用取模运算符过滤偶数：
```go
func FilterEven(numbers []int) []int {
    var result []int
    for _, num := range numbers {
        if num%2 == 0 {
            result = append(result, num)
        }
    }
    return result
}
```

## 提示5：通过预分配优化性能
为了获得更好的性能，当你知道大致大小时可以预先分配切片：
```go
func FilterEven(numbers []int) []int {
    // 预分配估计容量
    result := make([]int, 0, len(numbers)/2)
    for _, num := range numbers {
        if num%2 == 0 {
            result = append(result, num)
        }
    }
    return result
}
```

## 提示6：使用内置函数的FindMax替代方案
你也可以使用Go的sort包来进行比较：
```go
import "sort"

func FindMax(numbers []int) int {
    if len(numbers) == 0 {
        return 0
    }
    
    // 创建副本避免修改原数据
    temp := make([]int, len(numbers))
    copy(temp, numbers)
    sort.Ints(temp)
    
    return temp[len(temp)-1]
}
```

## 提示7：需要考虑的边界情况
在函数中始终处理边界情况：
```go
func FindMax(numbers []int) int {
    if len(numbers) == 0 {
        return 0 // 或作为错误处理
    }
    // 正确处理负数
    max := numbers[0] // 不要假设最大值为0
    for _, num := range numbers[1:] {
        if num > max {
            max = num
        }
    }
    return max
}
```

## 关键切片概念：
- **范围循环**：使用 `for _, val := range slice` 进行遍历
- **切片创建**：使用 `make([]int, length, capacity)` 进行分配
- **Map查找**：使用 `map[key]bool` 实现高效的重复项检查
- **切片复制**：使用 `copy(dest, src)` 避免修改原始数据
- **取模运算符**：使用 `%` 判断奇偶性
- **边界情况**：始终处理空切片和负数