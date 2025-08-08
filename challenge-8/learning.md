# Learning materials for a chat server using Channels

## Building concurrent applications with Channels

This challenge focuses on building a chat server using Go's concurrency primitives (goroutines and channels) to handle multiple clients simultaneously.

### Go's concurrency model

Go's concurrency model is based on CSP (Communicating Sequential Processes):
- **Goroutines**: Lightweight threads managed by the Go runtime
- **Channels**: Communication and synchronization between goroutines
- **"Do not communicate by sharing memory; share memory by communicating"**

### Networking fundamentals

The chat server communicates with clients using TCP connections:

```go
// Create a listener on a TCP port
listener, err := net.Listen("tcp", ":8080")
if err != nil {
    log.Fatal(err)
}
defer listener.Close()

// Accept new connections
for {
    conn, err := listener.Accept()
    if err != nil {
        log.Println("Error accepting connection:", err)
        continue
    }
    
    // Handle each connection in a goroutine
    go handleConnection(conn)
}
```

### Client handler pattern

Each client connection should be handled in its own goroutine:

```go
func handleConnection(conn net.Conn) {
    defer conn.Close()
    
    // Create a scanner to read messages line by line
    scanner := bufio.NewScanner(conn)
    
    // Read username
    var username string
    if scanner.Scan() {
        username = scanner.Text()
    }
    
    // Add client to chat
    client := &Client{
        Conn:     conn,
        Username: username,
        Outgoing: make(chan string),
    }
    chat.Join(client)
    
    // Set up bidirectional communication
    go client.ReadMessages(scanner, chat)
    client.WriteMessages()
}
```

### Broadcasting pattern using Channels

A central hub broadcasts messages to all connected clients:

```go
type Chat struct {
    clients    map[*Client]bool
    broadcast  chan string
    join       chan *Client
    leave      chan *Client
    mu         sync.Mutex
}

func NewChat() *Chat {
    return &Chat{
        clients:   make(map[*Client]bool),
        broadcast: make(chan string),
        join:      make(chan *Client),
        leave:     make(chan *Client),
    }
}

func (c *Chat) Run() {
    for {
        select {
        case client := <-c.join:
            c.mu.Lock()
            c.clients[client] = true
            c.mu.Unlock()
            c.broadcast <- fmt.Sprintf("%s has joined the chat", client.Username)
            
        case client := <-c.leave:
            c.mu.Lock()
            delete(c.clients, client)
            c.mu.Unlock()
            close(client.Outgoing)
            c.broadcast <- fmt.Sprintf("%s has left the chat", client.Username)
            
        case message := <-c.broadcast:
            c.mu.Lock()
            for client := range c.clients {
                select {
                case client.Outgoing <- message:
                    // Message sent successfully
                default:
                    // Client buffer full, remove client
                    delete(c.clients, client)
                    close(client.Outgoing)
                }
            }
            c.mu.Unlock()
        }
    }
}
```

### Client struct and methods

Each client needs to handle reading from and writing to the connection:

```go
type Client struct {
    Conn     net.Conn
    Username string
    Outgoing chan string
}

// ReadMessages reads messages from the client and sends them to the chat room
func (c *Client) ReadMessages(scanner *bufio.Scanner, chat *Chat) {
    defer func() {
        chat.leave <- c
    }()
    
    for scanner.Scan() {
        message := scanner.Text()
        if message == "/quit" {
            break
        }
        
        chat.broadcast <- fmt.Sprintf("%s: %s", c.Username, message)
    }
}

// WriteMessages sends messages from the chat room to the client
func (c *Client) WriteMessages() {
    for message := range c.Outgoing {
        fmt.Fprintln(c.Conn, message)
    }
}
```

### Using select for non-blocking channel operations

The `select` statement allows you to wait on multiple channel operations:

```go
select {
case message := <-messageChan:
    // Handle message
case client := <-joinChan:
    // Handle new client
case <-time.After(30 * time.Second):
    // Handle timeout
default:
    // Non-blocking path (executes only when others are unavailable)
}
```

### Timeouts and deadlines

Handling timeouts is crucial to prevent blocked connections:

```go
// Set read deadline
conn.SetReadDeadline(time.Now().Add(5 * time.Minute))

// Set write deadline
conn.SetWriteDeadline(time.Now().Add(10 * time.Second))

// Context timeout for graceful shutdown
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
server.Shutdown(ctx)
```

### Fan-out/fan-in pattern for message processing

For advanced message handling, messages can be processed concurrently:

```go
func processMessages(input <-chan string, workers int) <-chan string {
    output := make(chan string)
    
    // Fan out to worker goroutines
    for i := 0; i < workers; i++ {
        go func() {
            for message := range input {
                // Process message (e.g., check commands, filter bad words)
                processed := processMessage(message)
                output <- processed
            }
        }()
    }
    
    return output
}

func processMessage(message string) string {
    // Apply formatting, filtering, etc.
    return message
}
```

### Buffered vs unbuffered channels

Choose channel type based on requirements:

```go
// Unbuffered channel - sender blocks until receiver is ready
unbuffered := make(chan string)

// Buffered channel - blocks only when buffer is full
buffered := make(chan string, 10)
```

Considerations:
- Unbuffered channels provide synchronization points
- Buffered channels allow senders to continue when receivers aren't ready
- Buffer size should be based on expected load patterns

### Handling client disconnections gracefully

Handle unexpected client disconnections properly:

```go
func (c *Client) ReadMessages(scanner *bufio.Scanner, chat *Chat) {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Recovered from panic: %v", r)
        }
        chat.leave <- c
    }()
    
    for scanner.Scan() {
        message := scanner.Text()
        if message == "" {
            continue
        }
        
        chat.broadcast <- fmt.Sprintf("%s: %s", c.Username, message)
    }
    
    // Check for errors
    if err := scanner.Err(); err != nil {
        log.Printf("Error reading from %s: %v", c.Username, err)
    }
}
```

### Rate limiting

Prevent clients from sending too many messages to the chat room:

```go
// Create a rate limiter allowing 5 messages per second
limiter := rate.NewLimiter(5, 10)

// Use in client handler
if !limiter.Allow() {
    // Rate limit exceeded
    fmt.Fprintln(conn, "Rate limit exceeded. Please slow down.")
    continue
}
```

### Logging and monitoring

Add logging to track server activity:

```go
// Structured logging with context
log.Printf("Client connected: %s (%s)", client.Username, conn.RemoteAddr())
log.Printf("Broadcast: %s", message)
log.Printf("Client disconnected: %s disconnected after %v", client.Username, time.Since(client.ConnectedAt))

// Track active connections
log.Printf("Active connections: %d", len(chat.clients))
```

### Graceful shutdown

Implement proper server shutdown to avoid losing connections:

```go
func main() {
    // Set up signal handling
    stop := make(chan os.Signal, 1)
    signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
    
    // Start chat server
    chat := NewChat()
    go chat.Run()
    
    // Start TCP server
    listener, err := net.Listen("tcp", ":8080")
    if err != nil {
        log.Fatal(err)
    }
    
    // Accept connections in a separate goroutine
    go acceptConnections(listener, chat)
    
    // Wait for termination signal
    <-stop
    log.Println("Shutting down server...")
    
    // Notify all clients
    chat.broadcast <- "SERVER: Chat server is shutting down"
    
    // Give clients time to disconnect
    time.Sleep(2 * time.Second)
    listener.Close()
}
```

## Best practices for chat servers

1. **Use context for cancellation**: Propagate cancellation signals throughout the application
2. **Implement health checks**: Monitor server health and connection status
3. **Add authentication**: Verify user identity before allowing joining
4. **Use heartbeat detection**: Identify improperly closed client connections
5. **Handle backpressure**: Manage slow clients to prevent memory issues
6. **Add metrics collection**: Track message count, user count, and error rates

## Further reading

- [Go Concurrency Patterns: Pipelines and Cancellation](https://blog.golang.org/pipelines)
- [Go Concurrency Patterns: Context](https://blog.golang.org/context)
- [net package documentation](https://pkg.go.dev/net)
- [sync package documentation](https://pkg.go.dev/sync)