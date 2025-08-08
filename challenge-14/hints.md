# 挑战14提示：使用gRPC的微服务

## 提示1：gRPC服务实现结构
从带有适当错误处理的基本服务结构开始实现：
```go
import (
    "context"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

type userServiceServer struct {
    users map[string]*User // 用于演示的内存存储
}

func (s *userServiceServer) GetUser(ctx context.Context, req *GetUserRequest) (*GetUserResponse, error) {
    if req.UserId == "" {
        return nil, status.Errorf(codes.InvalidArgument, "用户ID是必需的")
    }
    
    user, exists := s.users[req.UserId]
    if !exists {
        return nil, status.Errorf(codes.NotFound, "未找到用户")
    }
    
    return &GetUserResponse{User: user}, nil
}
```

## 提示2：业务逻辑中的gRPC状态码
为不同错误情况使用适当的gRPC状态码：
```go
func (s *userServiceServer) ValidateUser(ctx context.Context, req *ValidateUserRequest) (*ValidateUserResponse, error) {
    user, exists := s.users[req.UserId]
    if !exists {
        return nil, status.Errorf(codes.NotFound, "未找到用户")
    }
    
    if !user.IsActive {
        return nil, status.Errorf(codes.PermissionDenied, "用户未激活")
    }
    
    return &ValidateUserResponse{IsValid: true}, nil
}

func (s *productServiceServer) CheckInventory(ctx context.Context, req *CheckInventoryRequest) (*CheckInventoryResponse, error) {
    product, exists := s.products[req.ProductId]
    if !exists {
        return nil, status.Errorf(codes.NotFound, "产品未找到")
    }
    
    if product.Stock < req.Quantity {
        return nil, status.Errorf(codes.ResourceExhausted, "库存不足")
    }
    
    return &CheckInventoryResponse{Available: true}, nil
}
```

## 提示3：设置带有拦截器的gRPC服务器
创建带有日志记录和身份验证拦截器的服务器：
```go
func StartUserService(port string) (*grpc.Server, error) {
    lis, err := net.Listen("tcp", ":"+port)
    if err != nil {
        return nil, err
    }
    
    server := grpc.NewServer(
        grpc.UnaryInterceptor(grpc_middleware.ChainUnaryServer(
            LoggingInterceptor,
            AuthInterceptor,
        )),
    )
    
    userService := &userServiceServer{
        users: make(map[string]*User),
    }
    // 在此处注册你的proto服务
    RegisterUserServiceServer(server, userService)
    
    go func() {
        server.Serve(lis)
    }()
    
    return server, nil
}
```

## 提示4：实现拦截器
为横切关注点创建拦截器：
```go
func LoggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    
    log.Printf("gRPC调用: %s 已启动", info.FullMethod)
    
    resp, err := handler(ctx, req)
    
    duration := time.Since(start)
    log.Printf("gRPC调用: %s 在 %v 内完成", info.FullMethod, duration)
    
    return resp, err
}

func AuthInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    // 跳过某些方法的身份验证
    if info.FullMethod == "/health/check" {
        return handler(ctx, req)
    }
    
    // 提取认证元数据
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Errorf(codes.Unauthenticated, "未提供元数据")
    }
    
    authHeaders := md.Get("authorization")
    if len(authHeaders) == 0 {
        return nil, status.Errorf(codes.Unauthenticated, "未提供授权头")
    }
    
    // 验证令牌（简化版）
    if authHeaders[0] != "Bearer valid-token" {
        return nil, status.Errorf(codes.Unauthenticated, "无效令牌")
    }
    
    return handler(ctx, req)
}
```

## 提示5：gRPC客户端实现
创建连接到服务的客户端：
```go
type UserServiceClient struct {
    conn   *grpc.ClientConn
    client UserServiceClient // 由生成的proto文件提供
}

func (c *UserServiceClient) GetUser(ctx context.Context, userID string) (*User, error) {
    // 添加认证元数据
    ctx = metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer valid-token")
    
    req := &GetUserRequest{UserId: userID}
    resp, err := c.client.GetUser(ctx, req)
    if err != nil {
        return nil, err
    }
    
    return resp.User, nil
}

func ConnectToServices(userServiceAddr, productServiceAddr string) (*UserServiceClient, *ProductServiceClient, error) {
    // 连接到用户服务
    userConn, err := grpc.Dial(userServiceAddr, grpc.WithInsecure())
    if err != nil {
        return nil, nil, fmt.Errorf("连接用户服务失败: %w", err)
    }
    
    userClient := &UserServiceClient{
        conn:   userConn,
        client: NewUserServiceClient(userConn),
    }
    
    // 类似地处理产品服务...
    
    return userClient, productClient, nil
}
```

## 提示6：服务编排
实现协调多个服务的订单服务：
```go
type OrderService struct {
    userClient    *UserServiceClient
    productClient *ProductServiceClient
}

func (s *OrderService) CreateOrder(ctx context.Context, userID, productID string, quantity int) (*Order, error) {
    // 步骤1：验证用户
    _, err := s.userClient.ValidateUser(ctx, userID)
    if err != nil {
        return nil, fmt.Errorf("用户验证失败: %w", err)
    }
    
    // 步骤2：检查库存
    _, err = s.productClient.CheckInventory(ctx, productID, quantity)
    if err != nil {
        return nil, fmt.Errorf("库存检查失败: %w", err)
    }
    
    // 步骤3：创建订单
    order := &Order{
        Id:        generateOrderID(),
        UserId:    userID,
        ProductId: productID,
        Quantity:  quantity,
        Status:    "created",
        CreatedAt: time.Now().Unix(),
    }
    
    return order, nil
}
```

## 提示7：跨服务的错误处理
同时处理gRPC错误和业务逻辑错误：
```go
func handleServiceError(err error) error {
    if err == nil {
        return nil
    }
    
    // 检查是否为gRPC状态错误
    if status, ok := status.FromError(err); ok {
        switch status.Code() {
        case codes.NotFound:
            return fmt.Errorf("资源未找到: %s", status.Message())
        case codes.PermissionDenied:
            return fmt.Errorf("访问被拒绝: %s", status.Message())
        case codes.ResourceExhausted:
            return fmt.Errorf("资源耗尽: %s", status.Message())
        default:
            return fmt.Errorf("服务错误: %s", status.Message())
        }
    }
    
    // 处理其他错误
    return fmt.Errorf("意外错误: %w", err)
}
```

## gRPC核心概念：
- **状态码**：使用适当的代码（NotFound、PermissionDenied等）
- **拦截器**：链式拦截器以处理横切关注点
- **元数据**：传递认证和上下文信息
- **错误处理**：区分传输错误与业务逻辑错误
- **服务发现**：让客户端连接到运行中的服务
- **上下文传播**：在服务边界之间传递上下文