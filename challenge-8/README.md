[查看排行榜](SCOREBOARD.md)

# 挑战 8：使用通道的聊天服务器

## 问题描述

使用 Go 的通道和协程实现一个简单的聊天服务器。该聊天服务器应允许多个客户端连接，向所有客户端广播消息，并支持客户端之间的私密消息传递。

## 要求

1. 实现一个 `ChatServer` 结构体，用于管理连接和消息路由：
   - 添加和移除客户端
   - 向所有客户端广播消息
   - 在特定客户端之间路由私密消息
   - 优雅地处理断开连接

2. 实现一个 `Client` 结构体，表示一个已连接的客户端：
   - 唯一的用户名
   - 入站消息通道
   - 出站消息通道
   - 连接状态

3. 使用通道来管理客户端与服务器之间的消息流动。

4. 使用协程实现并发，以同时处理多个客户端。

5. 创建测试用例，模拟多个客户端的连接/断开以及消息交换。

## 函数签名

```go
// ChatServer 管理客户端连接和消息路由
type ChatServer struct {
    // 你的实现在此处
}

// NewChatServer 创建一个新的聊天服务器实例
func NewChatServer() *ChatServer

// Connect 将新客户端添加到聊天服务器
func (s *ChatServer) Connect(username string) (*Client, error)

// Disconnect 从聊天服务器中移除客户端
func (s *ChatServer) Disconnect(client *Client)

// Broadcast 向所有已连接的客户端发送消息
func (s *ChatServer) Broadcast(sender *Client, message string)

// PrivateMessage 发送消息给特定客户端
func (s *ChatServer) PrivateMessage(sender *Client, recipient string, message string) error

// Client 表示一个已连接的聊天客户端
type Client struct {
    // 你的实现在此处
}

// Send 向客户端发送消息
func (c *Client) Send(message string)

// Receive 返回客户端的下一个消息（阻塞式）
func (c *Client) Receive() string
```

## 测试用例

你的实现应能处理以下测试场景：

1. 多个客户端连接到服务器
2. 向所有客户端广播消息
3. 在特定客户端之间发送私密消息
4. 客户端断开连接后重新连接
5. 对无效操作进行错误处理（例如，向不存在的客户端发送消息）
6. 并发操作（多个客户端同时发送/接收）

## 约束条件

- 所有操作必须是线程安全的
- 聊天服务器应能处理至少 100 个并发客户端
- 消息应按发送顺序交付
- 错误应被优雅处理，并提供有意义的错误信息
- 测试用例不应导致死锁或竞态条件

## 指导说明

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-8/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的结构体和方法。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-8/` 目录中运行以下命令：

```bash
go test -v
```

## 高级附加挑战

对于寻求额外挑战的人：

1. 实现消息历史功能，使客户端在连接时可以获取最后 N 条消息
2. 添加对“聊天室”的支持，允许客户端加入/离开特定房间
3. 实现超时功能，在指定时间段内无活动则断开空闲客户端
4. 添加对消息类型的支持（例如，文本、图片引用、系统通知）