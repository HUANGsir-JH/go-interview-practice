[查看排行榜](SCOREBOARD.md)

# 挑战 6：词频统计器

## 问题描述

编写一个函数 `CountWordFrequency`，该函数接收一个包含多个单词的字符串，并返回一个映射，其中每个键是一个单词，值是该单词在字符串中出现的次数。比较时应忽略大小写，即 "Hello" 和 "hello" 应被视为同一个单词。

## 函数签名

```go
func CountWordFrequency(text string) map[string]int
```

## 输入格式

- 一个字符串 `text`，包含由空格、标点符号或换行符分隔的多个单词。

## 输出格式

- 一个映射，键为小写的单词，值为频率计数。

## 约束条件

- 单词定义为字母和数字的连续序列。
- 所有单词在计数前应转换为小写。
- 忽略所有标点符号、空格及其他非字母数字字符。
- `0 <= len(text) <= 10000`

## 示例输入与输出

### 示例输入 1

```
"The quick brown fox jumps over the lazy dog."
```

### 示例输出 1

```
{
    "the": 2,
    "quick": 1,
    "brown": 1,
    "fox": 1,
    "jumps": 1,
    "over": 1,
    "lazy": 1,
    "dog": 1
}
```

### 示例输入 2

```
"Hello, hello! How are you doing today? Today is a great day."
```

### 示例输出 2

```
{
    "hello": 2,
    "how": 1,
    "are": 1,
    "you": 1,
    "doing": 1,
    "today": 2,
    "is": 1,
    "a": 1,
    "great": 1,
    "day": 1
}
```

## 操作说明

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-6/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** `CountWordFrequency` 函数。
- 通过运行测试文件在本地测试你的解决方案。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-6/` 目录下运行以下命令：

```bash
go test -v
```