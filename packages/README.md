# 包挑战 - 动态系统文档

此目录包含流行 Go 库和框架的特定包编码挑战。该系统设计为完全动态，允许轻松添加新包而无需更改代码。

## 可用包

### 🗄️ [GORM](./gorm/) - ORM 库
**5 个挑战** | 初学者到高级 | **6-8 小时**
- 数据库操作、关联、迁移、高级查询和泛型 API

### 🌐 [Gin](./gin/) - Web 框架  
**5 个挑战** | 初学者到高级 | **6-8 小时**
- HTTP 路由、中间件、认证、文件处理和测试

### ⚡ [Cobra](./cobra/) - CLI 框架
**4 个挑战** | 初学者到高级 | **4-6 小时**
- 命令行应用程序、标志、子命令、数据持久化和高级模式

*更多包即将上线...*

## 目录结构

```
packages/
├── {package-name}/
│   ├── package.json                    # 包元数据
│   ├── challenge-N-{name}/
│   │   ├── metadata.json              # 挑战元数据（可选）
│   │   ├── README.md                  # 挑战说明
│   │   ├── solution-template.go       # 用户代码模板
│   │   ├── solution-template_test.go  # 测试文件
│   │   ├── hints.md                   # 提示与技巧
│   │   └── submissions/               # 用户提交
│   │       └── {username}/
│   │           └── solution.go        # 用户的解决方案
│   └── ...
```

## 添加新包

### 1. 创建包目录
使用你的包名称创建新目录：
```bash
mkdir packages/{package-name}
```

### 2. 创建 package.json
在 `packages/{package-name}/package.json` 中定义包元数据：

```json
{
  "name": "package-name",
  "display_name": "包显示名称",
  "description": "包的简要描述",
  "version": "v1.0.0",
  "github_url": "https://github.com/owner/repo",
  "documentation_url": "https://package-docs.com",
  "stars": 10000,
  "category": "web|cli|database|other",
  "difficulty": "beginner_to_advanced",
  "prerequisites": ["basic_go", "http_concepts"],
  "learning_path": [
    "challenge-1-basic-feature",
    "challenge-2-advanced-feature"
  ],
  "tags": ["tag1", "tag2", "tag3"],
  "estimated_time": "4-6 小时",
  "real_world_usage": [
    "使用场景 1",
    "使用场景 2"
  ]
}
```

### 3. 创建挑战
针对学习路径中的每个挑战：

#### 挑战目录
```bash
mkdir packages/{package-name}/challenge-N-{name}
```

#### 必需文件

**README.md** - 挑战说明和指导
**solution-template.go** - 起始代码模板
**solution-template_test.go** - 测试用例
**hints.md** - 对学习者有帮助的提示

#### 可选 metadata.json
用于增强挑战信息：

```json
{
  "title": "挑战标题",
  "description": "详细描述",
  "short_description": "卡片上的简要描述",
  "difficulty": "初学者|中级|高级",
  "estimated_time": "30-45 分钟",
  "learning_objectives": [
    "目标 1",
    "目标 2"
  ],
  "prerequisites": ["前置条件1"],
  "tags": ["tag1", "tag2"],
  "real_world_connection": "如何在真实项目中应用",
  "requirements": [
    "要求 1",
    "要求 2"
  ],
  "bonus_points": [
    "加分任务 1"
  ],
  "icon": "bi-icon-name",
  "order": 1
}
```

## 动态系统工作原理

### 1. 包发现
- 系统自动扫描 `packages/` 目录
- 每个子目录被视为一个包
- 包元数据从 `package.json` 加载

### 2. 挑战加载
- 挑战从 `package.json` 的 `learning_path` 中发现
- 扫描挑战目录以获取内容
- 如果可用，则从 `metadata.json` 加载元数据
- 若无元数据，则根据目录名和 README 文件生成回退元数据

### 3. 模板函数
系统提供动态模板函数：
- `isPackageActive` - 检查包是否有可用挑战
- `getPackageChallenges` - 获取有序的挑战列表
- `getChallengeInfo` - 获取特定挑战的元数据
- `getDifficultyBadgeClass` - 获取难度的 CSS 类
- `getCategoryIcon` - 获取包类别的图标
- `isComingSoon` - 检查挑战是否尚未可用

### 4. 状态管理
挑战自动具有状态：
- **available** - 挑战目录存在且包含内容
- **coming-soon** - 挑战列在 learning_path 中但目录不存在

## 动态系统的优点

1. **零代码变更** - 添加包无需修改应用程序代码
2. **一致的 UI** - 所有包使用相同的模板渲染
3. **灵活的元数据** - 通过 JSON 实现丰富的挑战信息
4. **自动发现** - 新包立即出现
5. **回退支持** - 即使元数据最少也能运行，越多越完善
6. **易于维护** - 包特定逻辑包含在元数据中

## 包类别

- **web** - Web 框架和 HTTP 库
- **cli** - 命令行工具和框架  
- **database** - 数据库驱动和 ORM
- **other** - 通用库

## 图标

为挑战使用 Bootstrap 图标：
- `bi-play-circle` - 基础/入门挑战
- `bi-layers` - 中间件/架构
- `bi-shield-check` - 验证/安全
- `bi-person-lock` - 认证
- `bi-cloud-upload` - 文件处理
- `bi-database` - 数据库操作
- `bi-terminal` - CLI 操作
- `bi-code-slash` - 一般编码

## 最佳实践

1. **学习路径顺序** - 按从基础到高级排列挑战
2. **清晰的描述** - 编写有用且具体的挑战描述
3. **良好的测试覆盖** - 提供全面的测试用例
4. **实际示例** - 在挑战中使用真实场景
5. **渐进的难度** - 每个挑战应建立在前一个基础上
6. **有用的提示** - 提供提示但不泄露答案

## 贡献指南

有关包挑战的详细贡献指南，请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md#package-challenges-frameworklibrary-focused)。

### 快速指南

1. **遵循目录结构** - 使用上述所示的精确结构
2. **包含所有必需文件** - README.md、solution-template.go、测试文件和提示
3. **创建完整解决方案** - 在 submissions/RezaSi/ 中包含完整解决方案
4. **彻底测试** - 确保所有测试通过并覆盖边界情况
5. **编写清晰文档** - 提供全面的学习材料
6. **使用适当的难度** - 根据目标受众匹配难度
7. **确保学习目标** - 每个挑战应有明确的教育目标
8. **遵循包约定** - 使用一致的命名和结构
9. **包含依赖项** - 正确设置 go.mod 并包含所有所需包
10. **创建可执行脚本** - 提供 run_tests.sh 用于验证

### 包含的模板文件

系统提供以下模板文件：
- **metadata.json** - 挑战元数据结构
- **go.mod** - 包含依赖项的模块配置
- **solution-template.go** - 带有 TODO 的代码模板
- **solution-template_test.go** - 全面的测试套件
- **learning.md** - 教育内容（建议 400+ 行）
- **hints.md** - 分步指导
- **run_tests.sh** - 测试和验证脚本

系统将自动检测并显示你的新包挑战！