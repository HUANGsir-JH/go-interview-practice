[查看排行榜](SCOREBOARD.md)

# 挑战 2：反转字符串

## 问题描述

编写一个函数 `ReverseString`，该函数接受一个字符串并返回反转后的字符串。

## 函数签名

```go
func ReverseString(s string) string
```

## 输入格式

- 一行包含一个字符串 `s`。

## 输出格式

- 反转后的字符串。

## 约束条件

- `0 <= len(s) <= 1000`
- 字符串可能包含ASCII字母、数字和特殊字符。

## 示例输入和输出

### 示例输入 1

```
hello
```

### 示例输出 1

```
olleh
```

### 示例输入 2

```
Go is fun!
```

### 示例输出 2

```
!nuf si oG
```

## 操作说明

- **Fork** 仓库。
- **Clone** 您的 fork 到本地机器。
- **Create** 在 `challenge-2/submissions/` 内创建一个以您的 GitHub 用户名命名的目录。
- **Copy** 将 `solution-template.go` 文件复制到您的提交目录中。
- **Implement** 实现 `ReverseString` 函数。
- **Test** 通过运行测试文件在本地测试您的解决方案。
- **Commit** 并 **push** 您的代码到您的 fork。
- **Create** 创建拉取请求以提交您的解决方案。

## 在本地测试您的解决方案

1. **初始化Go模块**（如果尚未初始化）：

   导航到 `challenge-2` 目录：

   ```bash
   cd challenge-2
   go mod init challenge2
   ```

2. **运行测试：**

   ```bash
   go test -v
   ```