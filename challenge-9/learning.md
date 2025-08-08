# RESTful图书管理API学习资料

## 使用Go构建RESTful API

本挑战聚焦于实现一个用于管理图书的RESTful API，涵盖API设计、路由、JSON处理和数据库交互的核心概念。

### HTTP服务器基础

Go的标准库提供了构建HTTP服务器所需的一切：

```go
package main

import (
    "fmt"
    "log"
    "net/http"
)

func main() {
    // 定义路由处理器
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "你好，世界！")
    })
    
    // 启动服务器
    log.Println("服务器在 :8080 启动")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### RESTful API设计

REST（表述性状态转移）是一种用于设计网络应用的架构风格：

1. **资源**：通过URL标识（例如 `/books`，`/books/123`）
2. **HTTP方法**：用于执行操作
   - `GET`：获取资源
   - `POST`：创建新资源
   - `PUT`：更新现有资源
   - `DELETE`：删除资源
3. **表示形式**：通常为JSON或XML
4. **无状态性**：每个请求都包含所需的所有信息

### HTTP路由器

虽然Go的标准库包含基本路由功能，但像`gorilla/mux`这样的路由器包提供了更多灵活性：

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    
    "github.com/gorilla/mux"
)

func main() {
    r := mux.NewRouter()
    
    // 定义路由
    r.HandleFunc("/books", getBooks).Methods("GET")
    r.HandleFunc("/books", createBook).Methods("POST")
    r.HandleFunc("/books/{id}", getBook).Methods("GET")
    r.HandleFunc("/books/{id}", updateBook).Methods("PUT")
    r.HandleFunc("/books/{id}", deleteBook).Methods("DELETE")
    
    // 服务静态文件
    r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
    
    // 启动服务器
    log.Println("服务器在 :8080 启动")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

### JSON处理

Go使用`encoding/json`包轻松处理JSON：

```go
// 定义资源的结构体
type Book struct {
    ID     string `json:"id"`
    Title  string `json:"title"`
    Author string `json:"author"`
    Year   int    `json:"year"`
}

// 解析JSON请求体
func createBook(w http.ResponseWriter, r *http.Request) {
    var book Book
    
    // 从请求体中解码JSON
    decoder := json.NewDecoder(r.Body)
    if err := decoder.Decode(&book); err != nil {
        http.Error(w, "无效的请求负载", http.StatusBadRequest)
        return
    }
    defer r.Body.Close()
    
    // 生成唯一ID
    book.ID = uuid.New().String()
    
    // 保存图书（实现取决于你的存储方式）
    books = append(books, book)
    
    // 返回创建的图书
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(book)
}

// 返回JSON响应
func getBooks(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(books)
}
```

### 路由参数

从URL中提取参数：

```go
func getBook(w http.ResponseWriter, r *http.Request) {
    // 从URL获取ID
    vars := mux.Vars(r)
    id := vars["id"]
    
    // 查找图书
    for _, book := range books {
        if book.ID == id {
            w.Header().Set("Content-Type", "application/json")
            json.NewEncoder(w).Encode(book)
            return
        }
    }
    
    // 图书未找到
    http.Error(w, "图书未找到", http.StatusNotFound)
}
```

### 查询参数

解析查询参数以实现过滤、分页等功能：

```go
func getBooks(w http.ResponseWriter, r *http.Request) {
    // 获取查询参数
    query := r.URL.Query()
    
    // 按作者过滤（如果提供）
    author := query.Get("author")
    
    // 解析分页参数
    page, _ := strconv.Atoi(query.Get("page"))
    if page < 1 {
        page = 1
    }
    
    limit, _ := strconv.Atoi(query.Get("limit"))
    if limit < 1 || limit > 100 {
        limit = 10 // 默认限制
    }
    
    // 应用过滤和分页
    var result []Book
    // ... 实现细节 ...
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(result)
}
```

### 数据存储选项

多种存储图书数据的方式：

#### 1. 内存存储

简单但非持久化：

```go
var books []Book // 全局变量存储图书

// 添加图书
books = append(books, book)

// 查找图书
for i, book := range books {
    if book.ID == id {
        return book, i, nil
    }
}

// 更新图书
books[index] = updatedBook

// 删除图书
books = append(books[:index], books[index+1:]...)
```

#### 2. SQL数据库

使用`database/sql`包配合如`go-sql-driver/mysql`的驱动程序：

```go
import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
)

var db *sql.DB

func initDB() {
    var err error
    db, err = sql.Open("mysql", "user:password@tcp(127.0.0.1:3306)/bookstore")
    if err != nil {
        log.Fatal(err)
    }
    
    // 检查连接
    if err := db.Ping(); err != nil {
        log.Fatal(err)
    }
}

// 创建图书
func createBookDB(book Book) (string, error) {
    query := `INSERT INTO books (title, author, year) VALUES (?, ?, ?)`
    result, err := db.Exec(query, book.Title, book.Author, book.Year)
    if err != nil {
        return "", err
    }
    
    id, err := result.LastInsertId()
    return strconv.FormatInt(id, 10), err
}

// 获取所有图书
func getBooksDB() ([]Book, error) {
    query := `SELECT id, title, author, year FROM books`
    rows, err := db.Query(query)
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    
    var books []Book
    for rows.Next() {
        var book Book
        if err := rows.Scan(&book.ID, &book.Title, &book.Author, &book.Year); err != nil {
            return nil, err
        }
        books = append(books, book)
    }
    
    return books, nil
}
```

#### 3. NoSQL数据库

使用MongoDB官方Go驱动程序：

```go
import (
    "context"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/bson/primitive"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

var collection *mongo.Collection

func initMongoDB() {
    client, err := mongo.Connect(context.Background(), options.Client().ApplyURI("mongodb://localhost:27017"))
    if err != nil {
        log.Fatal(err)
    }
    
    collection = client.Database("bookstore").Collection("books")
}

// 创建图书
func createBookMongo(book Book) (string, error) {
    book.ID = primitive.NewObjectID().Hex()
    _, err := collection.InsertOne(context.Background(), book)
    return book.ID, err
}

// 获取所有图书
func getBooksMongo() ([]Book, error) {
    cursor, err := collection.Find(context.Background(), bson.M{})
    if err != nil {
        return nil, err
    }
    defer cursor.Close(context.Background())
    
    var books []Book
    if err := cursor.All(context.Background(), &books); err != nil {
        return nil, err
    }
    
    return books, nil
}
```

### 中间件

中间件函数在请求到达处理器之前进行处理：

```go
// 日志中间件
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %s", r.Method, r.RequestURI, time.Since(start))
    })
}

// 认证中间件
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "未授权", http.StatusUnauthorized)
            return
        }
        
        // 验证令牌...
        
        next.ServeHTTP(w, r)
    })
}

// 应用中间件
r := mux.NewRouter()
r.Use(loggingMiddleware)

// 仅对特定路由应用认证
protected := r.PathPrefix("/api").Subrouter()
protected.Use(authMiddleware)
protected.HandleFunc("/books", createBook).Methods("POST")
```

### 输入验证

验证传入的数据以确保其符合要求：

```go
func validateBook(book Book) error {
    if book.Title == "" {
        return errors.New("标题是必需的")
    }
    
    if book.Author == "" {
        return errors.New("作者是必需的")
    }
    
    if book.Year < 0 || book.Year > time.Now().Year() {
        return errors.New("无效的年份")
    }
    
    return nil
}

// 在处理器中使用
func createBook(w http.ResponseWriter, r *http.Request) {
    var book Book
    if err := json.NewDecoder(r.Body).Decode(&book); err != nil {
        http.Error(w, "无效的请求负载", http.StatusBadRequest)
        return
    }
    
    if err := validateBook(book); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    // 继续图书创建...
}
```

### 错误处理

一致的错误处理可提高API可用性：

```go
// 自定义错误响应
type ErrorResponse struct {
    StatusCode int    `json:"-"`
    Message    string `json:"message"`
    Error      string `json:"error,omitempty"`
}

// 响应错误的辅助函数
func respondWithError(w http.ResponseWriter, statusCode int, message string, err error) {
    response := ErrorResponse{
        StatusCode: statusCode,
        Message:    message,
    }
    
    if err != nil {
        response.Error = err.Error()
    }
    
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(statusCode)
    json.NewEncoder(w).Encode(response)
}

// 在处理器中的使用
func getBook(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    
    book, err := getBookByID(id)
    if err != nil {
        if err == ErrBookNotFound {
            respondWithError(w, http.StatusNotFound, "图书未找到", nil)
        } else {
            respondWithError(w, http.StatusInternalServerError, "获取图书失败", err)
        }
        return
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(book)
}
```

### CORS（跨域资源共享）

允许来自不同域名的请求：

```go
// CORS中间件
func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 设置CORS头
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        
        // 处理预检请求
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

// 应用中间件
r.Use(corsMiddleware)
```

### 测试REST API

使用Go的测试包测试API端点：

```go
func TestGetBooks(t *testing.T) {
    // 创建请求
    req, err := http.NewRequest("GET", "/books", nil)
    if err != nil {
        t.Fatal(err)
    }
    
    // 创建响应记录器
    rr := httptest.NewRecorder()
    
    // 创建处理器
    router := mux.NewRouter()
    router.HandleFunc("/books", getBooks).Methods("GET")
    
    // 处理请求
    router.ServeHTTP(rr, req)
    
    // 检查状态码
    if status := rr.Code; status != http.StatusOK {
        t.Errorf("处理器返回了错误的状态码：got %v 期望 %v", status, http.StatusOK)
    }
    
    // 检查响应体
    var books []Book
    if err := json.Unmarshal(rr.Body.Bytes(), &books); err != nil {
        t.Fatal(err)
    }
    
    // 验证响应
    if len(books) != 2 {
        t.Errorf("期望2本书，实际得到 %d", len(books))
    }
}
```

## RESTful API的最佳实践

1. **使用正确的HTTP状态码**：成功用200，创建用201，错误请求用400，未找到用404等。
2. **统一命名规范**：使用复数名词表示资源（例如 `/books` 而不是 `/book`）
3. **API版本控制**：在URL或头部包含版本号（例如 `/api/v1/books`）
4. **分页**：为大型集合实现分页
5. **过滤、排序和搜索**：通过查询参数支持
6. **文档**：使用Swagger等工具记录你的API

## 进一步阅读

- [RESTful API设计指南](https://restfulapi.net/)
- [Go Web示例](https://gowebexamples.com/)
- [使用Gorilla Mux构建RESTful API](https://www.digitalocean.com/community/tutorials/how-to-make-an-api-with-go-using-gorilla-mux)
- [Go数据库教程](https://tutorialedge.net/golang/golang-mysql-tutorial/)