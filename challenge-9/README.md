[查看排行榜](SCOREBOARD.md)

# 挑战 9：RESTful 图书管理系统 API

## 问题描述

使用 Go 语言实现一个图书管理系统的 RESTful API。该 API 应允许用户对图书执行 CRUD 操作，并使用内存数据库实现数据持久化。本挑战测试你设计和实现完整 Web 服务的能力，处理 HTTP 请求与响应，以及管理数据持久化。

## 要求

1. 实现以下端点的 RESTful API：
   - `GET /api/books`：获取所有图书
   - `GET /api/books/{id}`：根据 ID 获取特定图书
   - `POST /api/books`：创建新图书
   - `PUT /api/books/{id}`：更新现有图书
   - `DELETE /api/books/{id}`：删除图书
   - `GET /api/books/search?author={author}`：按作者搜索图书
   - `GET /api/books/search?title={title}`：按标题搜索图书

2. 实现一个 `Book` 结构体，包含以下字段：
   - `ID`：图书的唯一标识符
   - `Title`：图书标题
   - `Author`：图书作者
   - `PublishedYear`：图书出版年份
   - `ISBN`：国际标准书号
   - `Description`：图书简要描述

3. 使用 Go 数据结构实现内存数据库以存储图书。

4. 实现适当的错误处理和状态码：
   - 200 OK：GET、PUT、DELETE 成功
   - 201 Created：POST 成功
   - 400 Bad Request：输入无效
   - 404 Not Found：资源未找到
   - 500 Internal Server Error：服务器端错误

5. 所有端点均需实现输入验证。

6. API 应返回 JSON 格式的响应。

## 函数签名与接口

```go
// Book 表示数据库中的图书
type Book struct {
    ID            string `json:"id"`
    Title         string `json:"title"`
    Author        string `json:"author"`
    PublishedYear int    `json:"published_year"`
    ISBN          string `json:"isbn"`
    Description   string `json:"description"`
}

// BookRepository 定义图书数据访问的操作
type BookRepository interface {
    GetAll() ([]*Book, error)
    GetByID(id string) (*Book, error)
    Create(book *Book) error
    Update(id string, book *Book) error
    Delete(id string) error
    SearchByAuthor(author string) ([]*Book, error)
    SearchByTitle(title string) ([]*Book, error)
}

// BookService 定义图书操作的业务逻辑
type BookService interface {
    GetAllBooks() ([]*Book, error)
    GetBookByID(id string) (*Book, error)
    CreateBook(book *Book) error
    UpdateBook(id string, book *Book) error
    DeleteBook(id string) error
    SearchBooksByAuthor(author string) ([]*Book, error)
    SearchBooksByTitle(title string) ([]*Book, error)
}

// BookHandler 处理图书操作的 HTTP 请求
type BookHandler struct {
    Service BookService
}

// 在 BookHandler 上实现适当的方法以处理 HTTP 请求
```

## 项目结构

你的解决方案应遵循清晰的架构，实现关注点分离：

```
challenge-9/
├── submissions/
│   └── yourusername/
│       └── solution-template.go
├── api/
│   ├── handlers/
│   │   └── book_handler.go
│   └── middleware/
│       └── logger.go
├── domain/
│   └── models/
│       └── book.go
├── repository/
│   └── book_repository.go
├── service/
│   └── book_service.go
└── main.go
```

## 测试用例

你的解决方案应能处理以下测试场景：

1. 当数据库为空时获取所有图书
2. 使用有效数据创建新图书
3. 使用无效数据（缺少必填字段）创建新图书
4. 当图书存在时通过 ID 获取特定图书
5. 当图书不存在时通过 ID 获取特定图书
6. 使用有效数据更新图书
7. 更新不存在的图书
8. 删除存在的图书
9. 删除不存在的图书
10. 按作者搜索图书并返回结果
11. 按标题搜索图书但无结果

## 指令

- **Fork** 仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-9/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需组件。
- 通过运行测试文件在本地测试你的解决方案。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-9/` 目录下运行以下命令：

```bash
go test -v
```

## 额外挑战

对于寻求更高挑战的开发者：

1. 使用 JWT 添加认证和授权
2. 为 `GET /api/books` 端点实现分页功能
3. 添加速率限制中间件
4. 为图书查询添加过滤和排序选项
5. 为 API 添加 Swagger 文档