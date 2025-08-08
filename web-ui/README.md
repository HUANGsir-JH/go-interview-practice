# Go面试实战Web UI

这是Go面试实战项目的基于Web的用户界面，为解决Go编程挑战提供了一个交互式环境。

## 功能特点

- **挑战浏览器**：查看所有可用的编程挑战，带有难度指示器。
- **浏览器内代码编辑器**：直接在浏览器中编辑和运行Go代码，具有语法高亮功能。
- **测试运行器**：针对您的解决方案运行测试，并实时查看结果。
- **学习材料**：访问每个挑战特定的Go学习材料，以提高您的理解。
- **排行榜**：跟踪您的进度，看看您与其他人的比较情况。
- **Markdown支持**：挑战描述和学习材料具有完整的Markdown支持。

## 开始使用

### 前置要求

- Go 1.16 或更高版本
- Web浏览器（Chrome、Firefox、Safari、Edge）

### 运行Web UI

1. 导航到web-ui目录：
   ```
   cd web-ui
   ```

2. 运行Web服务器：
   ```
   go run main.go
   ```

3. 打开浏览器并访问：
   ```
   http://localhost:8080
   ```

## 项目结构

```
web-ui/
├── main.go                  # 主服务器入口点
├── static/                  # 静态资源
│   ├── css/                 # CSS样式表
│   │   └── style.css        # UI的自定义CSS
│   └── js/                  # JavaScript文件
│       └── main.js          # 通用JavaScript工具
├── templates/               # HTML模板
│   ├── base.html            # 具有通用布局的基础模板
│   ├── challenge.html       # 带有代码编辑器的挑战页面
│   ├── home.html            # 带有挑战列表的主页
│   └── scoreboard.html      # 结果的排行榜页面
└── README.md                # 本文件
```

## 技术细节

### 模板和HTML渲染

Web UI使用Go的`html/template`包进行服务器端渲染，具有定义通用布局的基础模板和每种页面类型的单独内容模板。

### JavaScript库

- **Bootstrap**：用于响应式UI组件
- **Ace Editor**：用于浏览器内代码编辑器
- **Marked**：用于Markdown解析
- **Highlight.js**：用于语法高亮

### API端点

Web UI暴露以下API端点：

- `GET /api/challenges`：获取所有挑战
- `GET /api/challenges/{id}`：获取特定挑战
- `POST /api/run`：运行特定挑战的代码
- `POST /api/submissions`：提交解决方案
- `GET /api/scoreboard/{id}`：获取挑战的排行榜

## 开发

### 添加新功能

1. 如果添加新页面，请在`templates`目录中创建新模板。
2. 在`main.go`中添加任何新的API处理程序。
3. 将CSS样式添加到`static/css/style.css`。
4. 将JavaScript工具添加到`static/js/main.js`。

### 开发模式运行

要在开发期间启用热重载，您可以使用[Air](https://github.com/cosmtrek/air)等工具：

```bash
# 安装Air
go install github.com/cosmtrek/air@latest

# 使用热重载运行
air
```

## 贡献

欢迎改进Web UI的贡献！请随时提交拉取请求或为新功能或错误修复打开问题。

## 许可证

本项目根据MIT许可证许可 - 详见LICENSE文件。

## 完整工作流程：从Fork到Pull Request

### 前置要求
1. **在GitHub上Fork仓库**（点击"Fork"按钮）
2. **在本地Clone您的fork**：`git clone https://github.com/yourusername/go-interview-practice.git`
3. **如上所述启动Web UI**

### 解决和提交挑战

1. **从主页选择一个挑战**
2. **在代码编辑器中编写您的解决方案**
3. **使用"运行测试"按钮测试您的代码**
4. **测试通过时提交您的解决方案**

### 成功提交后

Web UI将指导您完成以下步骤：

1. **保存到文件系统**：点击按钮在本地保存您的解决方案
2. **提交和推送**：
   ```bash
   git add challenge-X/submissions/yourusername/
   git commit -m "Add solution for Challenge X by yourusername"
   git push origin main
   ```
3. **创建拉取请求**：
   - 转到您在GitHub上的fork
   - 点击"Contribute" → "Open pull request"
   - 添加描述性标题
   - 提交PR

### 接下来会发生什么

- 您的拉取请求将被审核
- 一旦合并，您的解决方案将出现在公共排行榜上
- 您因解决挑战而获得学分
- 其他开发人员可以从您的方法中学习

这个工作流程确保：
- ✅ 您的解决方案得到正确跟踪
- ✅ 您为社区做出贡献
- ✅ 您的GitHub个人资料显示您的贡献
- ✅ 您出现在公共排行榜上

## 提交过程

Web UI提供两种提交解决方案的方式：

### 1. 浏览器内提交（仅用于排行榜）

当您点击"提交解决方案"按钮时，您的解决方案将：
- 针对挑战测试用例进行测试
- 如果所有测试通过，则添加到内存排行榜中
- 显示在挑战排行榜中

此提交是临时的，仅存在于当前服务器会话中。它不会将您的解决方案保存到文件系统中。

### 2. 文件系统提交（用于拉取请求）

成功提交通过所有测试的解决方案后，您将看到两个选项：

#### 选项1：一键文件系统保存

点击"保存到文件系统"按钮以：
- 在本地存储库中自动创建提交目录
- 将您的解决方案保存到`challenge-X/submissions/yourusername/solution-template.go`
- 获取提交和推送更改的Git命令列表

此选项创建GitHub拉取请求所需的实际文件结构。

#### 选项2：复制手动命令

如果您更喜欢自己管理文件创建，您可以：
- 点击"复制命令"将shell命令复制到剪贴板
- 在终端中运行这些命令以创建提交文件
- 使用提供的Git命令提交和推送更改

### 完成您的提交

将解决方案保存到文件系统后（通过任一方法），通过以下方式完成提交：
1. 提交您的更改
2. 推送到您的fork
3. 创建到原始存储库的拉取请求

这个工作流程确保您的提交正确集成到项目的审核系统中。