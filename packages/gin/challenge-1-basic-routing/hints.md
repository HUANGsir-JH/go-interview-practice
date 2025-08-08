# 挑战1：使用Gin进行基础路由的提示

## 提示1：设置基础路由器

从基本的Gin路由器设置开始：

```go
router := gin.Default()
```

`gin.Default()` 创建一个带有默认中间件（日志记录和恢复）的路由器。在生产环境中，你可以使用 `gin.New()` 来获得一个干净的路由器。

## 提示2：定义你的路由处理器

为每个端点创建处理器函数：

```go
func getUsers(c *gin.Context) {
    // 将 users 切片以 JSON 格式返回
    c.JSON(200, users)
}

func createUser(c *gin.Context) {
    // 将 JSON 绑定到 User 结构体并添加到 users 切片中
}
```

## 提示3：路由结构模式

使用 HTTP 方法函数来定义路由：

```go
router.GET("/users", getUsers)
router.POST("/users", createUser)
router.GET("/users/:id", getUserByID)
router.PUT("/users/:id", updateUser)
router.DELETE("/users/:id", deleteUser)
```

## 提示4：处理URL参数

对于包含参数的路由如 `/users/:id`，使用以下方式访问参数：

```go
func getUserByID(c *gin.Context) {
    id := c.Param("id")
    // 将 id 转换为整数并查找用户
    userID, _ := strconv.Atoi(id)
    for _, user := range users {
        if user.ID == userID {
            c.JSON(200, user)
            return
        }
    }
    c.JSON(404, gin.H{"error": "用户未找到"})
}
```

## 提示5：绑定JSON输入

对于 POST/PUT 请求，将 JSON 请求体绑定到你的结构体：

```go
func createUser(c *gin.Context) {
    var newUser User
    if err := c.ShouldBindJSON(&newUser); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    newUser.ID = len(users) + 1
    users = append(users, newUser)
    c.JSON(201, newUser)
}
```

## 提示6：启动服务器

别忘了在指定端口上启动服务器：

```go
router.Run(":8080")
```