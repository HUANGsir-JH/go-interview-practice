[查看排行榜](SCOREBOARD.md)

# 挑战 14：使用 gRPC 的微服务

在此挑战中，你将使用 gRPC 概念实现微服务架构，用于服务间通信。你将创建一个用户服务和一个产品服务，它们协同工作以提供订单管理系统。

## 学习目标

- 理解微服务架构原则
- 学习 gRPC 概念及错误处理
- 实现服务间通信
- 练习使用 gRPC 拦截器处理横切关注点
- 处理基于网络的服务交互

## 要求

在 `solution-template.go` 中实现以下 TODO 方法：

### 1. 服务业务逻辑
- `UserServiceServer.GetUser()`: 根据 ID 获取用户，并进行适当的错误处理
- `UserServiceServer.ValidateUser()`: 检查用户是否存在且处于激活状态
- `ProductServiceServer.GetProduct()`: 根据 ID 获取产品，并进行适当的错误处理
- `ProductServiceServer.CheckInventory()`: 检查产品库存情况

### 2. 订单服务
- `OrderService.CreateOrder()`: 协调用户验证、产品检查和订单创建

### 3. gRPC 基础设施
- `StartUserService()`: 设置并启动带有拦截器的用户服务
- `StartProductService()`: 设置并启动带有拦截器的产品服务
- `ConnectToServices()`: 创建客户端并连接到两个服务

### 4. gRPC 客户端
- `UserServiceClient.GetUser()`: 向用户服务发起 gRPC 调用
- `UserServiceClient.ValidateUser()`: 执行用户验证的 gRPC 调用
- `ProductServiceClient.GetProduct()`: 向产品服务发起 gRPC 调用
- `ProductServiceClient.CheckInventory()`: 执行库存检查的 gRPC 调用

### 5. 拦截器
- `LoggingInterceptor`: 记录方法调用及执行时间
- `AuthInterceptor`: 在请求中添加认证元数据

## 涉及的关键概念

- **gRPC 状态码**：使用适当的状态码（如 NotFound、PermissionDenied 等）
- **服务接口**：服务逻辑与传输机制之间的清晰分离
- **网络通信**：真实的跨服务调用
- **错误传播**：在服务边界之间正确处理错误
- **拦截器**：日志记录和认证等横切关注点
- **微服务模式**：服务编排与协调

## 提示

- 使用 `status.Errorf()` 返回正确的 gRPC 错误
- 记住要同时处理业务逻辑错误和网络错误
- 服务应验证输入并返回适当的错误码
- OrderService 协调对用户服务和产品服务的调用
- 拦截器包装所有服务调用以实现日志记录/认证

## 运行测试

```bash
go test -v
```

测试将：
1. 启动各个服务并测试其功能
2. 通过 OrderService 测试服务间通信
3. 验证各种场景下的错误处理是否正确
4. 检查拦截器是否正常工作

## 示例 gRPC 状态码

- `codes.OK`: 操作成功
- `codes.NotFound`: 资源不存在
- `codes.PermissionDenied`: 用户未授权
- `codes.ResourceExhausted`: 库存不足
- `codes.InvalidArgument`: 输入参数无效

完成所有 TODO 方法以使测试通过！