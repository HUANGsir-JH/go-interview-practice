[查看排行榜](SCOREBOARD.md)

# 挑战 13：使用 Go 操作 SQL 数据库

在此挑战中，你将使用 Go 和 SQL 实现一个产品库存系统。你需要创建与 SQLite 数据库交互的函数，对产品执行 CRUD 操作（创建、读取、更新、删除）。

## 要求

1. 创建一个包含 `products` 表的 SQLite 数据库  
2. 实现以下函数：  
   - `CreateProduct` - 将新产品添加到数据库  
   - `GetProduct` - 根据 ID 获取产品  
   - `UpdateProduct` - 更新产品的详细信息  
   - `DeleteProduct` - 删除产品  
   - `ListProducts` - 列出所有产品，支持可选过滤  
3. 确保对数据库操作进行适当的错误处理  
4. 为修改多个记录的操作实现事务支持  
5. 使用参数绑定以防止 SQL 注入  
6. 包含的测试文件包含检查所有 CRUD 操作和错误处理的场景