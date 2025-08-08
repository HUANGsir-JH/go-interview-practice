# 聊天服务器使用 Channels 的提示

## 提示 1：ChatServer 结构
设计你的 ChatServer 时，使用 channels 进行协调，并用 map 来跟踪客户端：
```go
type ChatServer struct {
    clients     map[string]*Client
    broadcast   chan BroadcastMessage
    connect     chan *Client
    disconnect  chan *Client
    mutex       sync.RWMutex
}
```

## 提示 2：Client 结构
每个客户端都需要用于通信的 channels 和标识信息：
```go
type Client struct {
    Username string
    Messages chan string
    server   *ChatServer
}
```

## 提示 3：消息类型
定义不同操作的消息结构：
```go
type BroadcastMessage struct {
    Sender  *Client
    Content string
}
```

## 提示 4：服务器事件循环
服务器应运行一个 goroutine，通过 channels 处理所有操作：
```go
func (s *ChatServer) run() {
    for {
        select {
        case client := <-s.connect:
            // 处理新连接
        case client := <-s.disconnect:
            // 处理断开连接
        case msg := <-s.broadcast:
            // 处理广播消息
        }
    }
}
```

## 提示 5：线程安全的客户端管理
访问 clients map 时使用 mutex：
```go
s.mutex.Lock()
s.clients[client.Username] = client
s.mutex.Unlock()
```

## 提示 6：Connect 方法实现
创建新客户端并通过 connect channel 发送：
```go
func (s *ChatServer) Connect(username string) (*Client, error) {
    if /* 用户名已存在 */ {
        return nil, errors.New("用户名已被占用")
    }
    
    client := &Client{
        Username: username,
        Messages: make(chan string, 100), // 缓冲 channel
        server:   s,
    }
    
    s.connect <- client
    return client, nil
}
```

## 提示 7：广播实现
通过 broadcast channel 发送消息：
```go
func (s *ChatServer) Broadcast(sender *Client, message string) {
    s.broadcast <- BroadcastMessage{
        Sender:  sender,
        Content: message,
    }
}
```

## 提示 8：私信实现
查找接收者并直接将消息发送到其 channel：
```go
func (s *ChatServer) PrivateMessage(sender *Client, recipient string, message string) error {
    s.mutex.RLock()
    client, exists := s.clients[recipient]
    s.mutex.RUnlock()
    
    if !exists {
        return errors.New("未找到接收者")
    }
    
    select {
    case client.Messages <- message:
        return nil
    default:
        return errors.New("接收者的消息队列已满")
    }
}
```

## 提示 9：客户端发送与接收方法
```go
func (c *Client) Send(message string) {
    select {
    case c.Messages <- message:
    default:
        // Channel 已满，优雅处理
    }
}

func (c *Client) Receive() string {
    return <-c.Messages
}
```

## 提示 10：优雅关闭
断开连接时，清理资源并关闭客户端的消息 channel：
```go
close(client.Messages)
delete(s.clients, client.Username)
```