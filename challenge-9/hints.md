# RESTful图书管理API使用提示

## 提示1：HTTP处理器结构
为每个端点使用 `http.HandlerFunc`，并通过多路复用器进行路由：
```go
func (h *BookHandler) SetupRoutes() *http.ServeMux {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/books", h.handleBooks)
    mux.HandleFunc("/api/books/", h.handleBookByID)
    mux.HandleFunc("/api/books/search", h.handleSearch)
    return mux
}
```

## 提示2：基于方法的路由
在处理器中处理不同的HTTP方法：
```go
func (h *BookHandler) handleBooks(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        h.getAllBooks(w, r)
    case http.MethodPost:
        h.createBook(w, r)
    default:
        http.Error(w, "方法不允许", http.StatusMethodNotAllowed)
    }
}
```

## 提示3：JSON响应辅助函数
创建用于JSON响应的辅助函数：
```go
func writeJSONResponse(w http.ResponseWriter, data interface{}, status int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}
```

## 提示4：请求体解析
解析JSON请求体：
```go
func (h *BookHandler) createBook(w http.ResponseWriter, r *http.Request) {
    var book Book
    if err := json.NewDecoder(r.Body).Decode(&book); err != nil {
        http.Error(w, "无效的JSON", http.StatusBadRequest)
        return
    }
    // 验证并创建图书
}
```

## 提示5：内存仓库实现
使用map实现仓库：
```go
type InMemoryBookRepository struct {
    books map[string]*Book
    mutex sync.RWMutex
}

func (r *InMemoryBookRepository) GetByID(id string) (*Book, error) {
    r.mutex.RLock()
    defer r.mutex.RUnlock()
    
    book, exists := r.books[id]
    if !exists {
        return nil, errors.New("未找到图书")
    }
    return book, nil
}
```

## 提示6：URL参数提取
从URL路径中提取ID：
```go
func extractIDFromPath(path string) string {
    parts := strings.Split(path, "/")
    if len(parts) >= 4 {
        return parts[3] // /api/books/{id}
    }
    return ""
}
```

## 提示7：查询参数处理
处理搜索参数：
```go
func (h *BookHandler) handleSearch(w http.ResponseWriter, r *http.Request) {
    author := r.URL.Query().Get("author")
    title := r.URL.Query().Get("title")
    
    if author != "" {
        books, err := h.Service.SearchBooksByAuthor(author)
        // 处理结果
    } else if title != "" {
        books, err := h.Service.SearchBooksByTitle(title)
        // 处理结果
    }
}
```

## 提示8：输入验证
验证必填字段：
```go
func validateBook(book *Book) error {
    if book.Title == "" {
        return errors.New("标题是必需的")
    }
    if book.Author == "" {
        return errors.New("作者是必需的")
    }
    if book.PublishedYear <= 0 {
        return errors.New("出版年份必须为正数")
    }
    return nil
}
```

## 提示9：搜索实现
实现不区分大小写的搜索：
```go
func (r *InMemoryBookRepository) SearchByAuthor(author string) ([]*Book, error) {
    r.mutex.RLock()
    defer r.mutex.RUnlock()
    
    var results []*Book
    lowerAuthor := strings.ToLower(author)
    
    for _, book := range r.books {
        if strings.Contains(strings.ToLower(book.Author), lowerAuthor) {
            results = append(results, book)
        }
    }
    return results, nil
}
```

## 提示10：错误响应结构
创建一致的错误响应格式：
```go
type ErrorResponse struct {
    Error   string `json:"error"`
    Message string `json:"message"`
}

func writeErrorResponse(w http.ResponseWriter, message string, status int) {
    response := ErrorResponse{
        Error:   http.StatusText(status),
        Message: message,
    }
    writeJSONResponse(w, response, status)
}
```