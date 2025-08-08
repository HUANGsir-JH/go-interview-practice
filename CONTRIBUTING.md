# **为Go面试实战做贡献**

感谢您对为 **Go面试实战** 仓库做贡献的兴趣！我们欢迎社区的贡献来帮助改进这个项目。无论您是想提交解决方案、添加新挑战还是改进文档，我们都非常感谢您的努力。

## **目录**

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
  - [提交解决方案](#提交解决方案)
  - [添加新挑战](#添加新挑战)
    - [经典挑战 vs 包挑战](#经典挑战-vs-包挑战)
    - [经典挑战](#经典挑战算法数据结构重点)
    - [包挑战](#包挑战框架库重点)
- [风格指南](#风格指南)
- [拉取请求流程](#拉取请求流程)
- [报告问题](#报告问题)
- [联系方式](#联系方式)

---

## **行为准则**

请注意，本项目附有[贡献者行为准则](CODE_OF_CONDUCT.md)。通过参与本项目，您同意遵守其条款。

---

## **如何贡献**

### **提交解决方案**

您可以向经典挑战和包挑战提交解决方案：

#### **对于经典挑战**

1. **Fork 仓库：**

   - 点击仓库页面上的"Fork"按钮。

2. **Clone 您的 Fork：**

   ```bash
   git clone https://github.com/yourusername/go-interview-practice.git
   ```

3. **创建新分支：**

   ```bash
   git checkout -b challenge-[number]-solution
   ```

4. **设置您的提交：**

   - 使用提供的脚本设置您的提交：

     ```bash
     ./create_submission.sh [challenge-number]
     ```

5. **实现您的解决方案：**

   - 编辑您提交目录中的 `solution-template.go` 文件。
   - 确保您的代码通过所有测试。

6. **本地运行测试：**

   - 导航到挑战目录并使用 `run_tests.sh`：

     ```bash
     cd challenge-[number]
     ./run_tests.sh
     ```

7. **提交和推送：**

   ```bash
   git add challenge-[number]/submissions/yourusername/
   git commit -m "Add Challenge [number] solution by [yourusername]"
   git push origin challenge-[number]-solution
   ```

#### **对于包挑战**

1. **Fork 和 Clone**（同上）

2. **创建新分支：**

   ```bash
   git checkout -b package-[package-name]-challenge-[number]-solution
   ```

3. **导航到包挑战：**

   ```bash
   cd packages/[package-name]/challenge-[number]-[topic]
   ```

4. **创建您的提交目录：**

   ```bash
   mkdir -p submissions/yourusername
   ```

5. **实现您的解决方案：**

   - 将 `solution-template.go` 复制到您的提交目录：

     ```bash
     cp solution-template.go submissions/yourusername/solution.go
     ```

   - 编辑 `submissions/yourusername/solution.go` 并完成所有 TODO。
   - 确保您的解决方案遵循包要求并通过所有测试。

6. **本地运行测试：**

   - 使用包挑战测试脚本：

     ```bash
     ./run_tests.sh
     # 提示时，输入您的 GitHub 用户名
     ```

7. **提交和推送：**

   ```bash
   git add packages/[package-name]/challenge-[number]-[topic]/submissions/yourusername/
   git commit -m "Add [Package] Challenge [number] solution by [yourusername]"
   git push origin package-[package-name]-challenge-[number]-solution
   ```

#### **通用提交指南**

8. **创建拉取请求：**

   - 转到您在 GitHub 上的 fork 并向 `main` 分支打开拉取请求。
   - 使用描述性标题并提及您解决了哪个挑战。

9. **接收反馈：**

   - 自动化测试将在您的拉取请求上运行。
   - 处理任何评论或请求的更改。
   - 包挑战解决方案将在合并时自动添加到排行榜。

### **添加新挑战**

您可以贡献两种类型的挑战：

#### **经典挑战 vs 包挑战**

在贡献新挑战之前，了解两种类型之间的区别很重要：

**经典挑战：**
- **重点：** 算法和数据结构问题
- **目的：** 基础编程概念和问题解决技能
- **结构：** 单个挑战目录，包含独立问题
- **示例：** 二分查找、链表操作、动态规划
- **目标受众：** 所有开发人员，无论框架经验如何
- **位置：** 根目录中的 `challenge-[number]/` 目录

**包挑战：**
- **重点：** 使用特定Go包/框架的真实应用程序开发
- **目的：** 构建生产应用程序的实用技能
- **结构：** 基于包的目录，包含渐进式挑战系列
- **示例：** 使用Gin的REST API、使用Cobra的CLI工具、使用GORM的数据库操作
- **目标受众：** 学习特定框架或构建作品集项目的开发人员
- **位置：** `packages/[package-name]/challenge-[number]-[topic]/` 目录

**何时选择每种类型：**

- 选择**经典挑战**用于：
  - 编程面试中的算法问题
  - 数据结构实现
  - 数学或逻辑谜题
  - 与语言无关的编程概念

- 选择**包挑战**用于：
  - 框架特定的教程
  - 构建完整的应用程序
  - 学习行业标准库
  - 展示真实世界的开发模式

#### **经典挑战（算法/数据结构重点）**

对于传统的算法和数据结构挑战：

1. **创建新问题：**

   - 打开一个问题来讨论新挑战的想法。
   - 提供问题陈述及其相关性等详细信息。

2. **等待批准：**

   - 等待维护者或社区成员提供反馈。

3. **创建新分支：**

   ```bash
   git checkout -b add-challenge-[number]
   ```

4. **设置挑战目录：**

   ```
   challenge-[number]/
   ├── README.md
   ├── solution-template.go
   ├── solution-template_test.go
   ├── learning.md
   ├── hints.md
   ├── run_tests.sh
   └── submissions/
   ```

5. **编写挑战描述：**

   - 在 `README.md` 中包含问题陈述、函数签名、输入/输出格式、约束和示例输入/输出。

6. **创建学习材料：**

   - 在 `challenge-[number]/learning.md` 中提供：
     - 挑战所需的相关Go概念的解释
     - 演示这些概念的代码示例
     - 最佳实践和效率考虑
     - 进一步阅读资源的链接

7. **创建解决方案模板：**

   - 在 `solution-template.go` 中提供带有适当注释的骨架代码。

8. **编写全面测试：**

   - 创建 `solution-template_test.go`，包含涵盖各种场景（包括边缘情况）的详细测试用例。

9. **创建提示：**

   - 在 `hints.md` 中提供逐步指导，但不给出完整解决方案。

10. **创建测试脚本：**

    - 创建可执行的 `run_tests.sh` 脚本来测试提交。

11. **更新文档：**

    - 将新挑战添加到主 `README.md`。

#### **包挑战（框架/库重点）**

对于专注于特定Go包/框架的挑战：

1. **创建新问题：**

   - 打开一个问题来讨论新的包挑战想法。
   - 指定包/框架（例如，Gin、Cobra、GORM）和挑战重点。

2. **等待批准：**

   - 等待维护者或社区成员提供反馈。

3. **创建新分支：**

   ```bash
   git checkout -b add-package-[package-name]-challenge-[number]
   ```

4. **设置包挑战目录：**

   ```
   packages/[package-name]/
   ├── package.json                    # 包元数据和学习路径
   └── challenge-[number]-[topic]/
       ├── metadata.json               # 挑战特定的元数据
       ├── README.md                   # 挑战描述
       ├── solution-template.go        # 带有TODO的模板
       ├── solution-template_test.go   # 全面测试
       ├── go.mod                      # 带有依赖项的模块
       ├── go.sum                      # 依赖项校验和
       ├── learning.md                 # 深入教育内容
       ├── hints.md                    # 逐步指导
       ├── run_tests.sh               # 测试脚本
       ├── SCOREBOARD.md              # 自动生成的排行榜
       └── submissions/               # 用户解决方案
           └── [username]/
               └── solution.go        # 完整的工作解决方案
   ```

5. **创建包元数据（如果是新包）：**

   - 创建 `packages/[package-name]/package.json`，包含：
     - 包信息（名称、描述、GitHub仓库）
     - 定义挑战进度的学习路径
     - 类别和难度级别

6. **创建挑战元数据：**

   - 创建 `metadata.json`，包含：
     - 标题、描述、难度、估计时间
     - 学习目标和先决条件
     - 要求和奖励积分
     - 标签和真实世界连接

7. **编写挑战描述：**

   - 在 `README.md` 中包含实际问题陈述、CLI/API要求和测试说明。

8. **创建学习材料：**

   - 在 `learning.md` 中提供全面的教育内容（400+行）：
     - 框架基础和核心概念
     - 代码示例和模式
     - 最佳实践和真实世界用法
     - 高级功能和测试策略

9. **创建解决方案模板：**

   - 在 `solution-template.go` 中提供结构化模板，包含：
     - 适当的导入和依赖项
     - 类型定义和结构
     - 带有TODO注释的函数签名
     - 辅助函数和验证逻辑

10. **编写全面测试：**

    - 创建 `solution-template_test.go`，包含：
      - 所有功能和特性的单元测试
      - 完整工作流程的集成测试
      - 边缘情况和错误场景
      - 性能和行为验证

11. **创建依赖项：**

    - 使用适当的模块名称和Go版本设置 `go.mod`
    - 包含包所需的所有依赖项
    - 运行 `go mod tidy` 生成 `go.sum`

12. **创建提示：**

    - 在 `hints.md` 中提供详细指导，包含：
      - 逐步实现指导
      - 代码示例和模式
      - 要避免的常见陷阱
      - 测试和调试技巧

13. **创建测试脚本：**

    - 创建可执行的 `run_tests.sh` 脚本，它：
      - 测试编译和功能
      - 运行单元测试和功能测试
      - 验证标志处理和参数处理
      - 提供详细反馈和后续步骤

14. **创建工作解决方案：**

    - 在 `submissions/RezaSi/solution.go` 中实现完整的工作解决方案
    - 确保它通过所有测试并展示最佳实践

15. **更新文档：**

    - 使用包排行榜脚本更新包排行榜
    - 确保Web UI可以发现并显示新挑战

### **两种挑战类型的通用指南**

12. **提交和推送：**

    ```bash
    # 对于经典挑战
    git add challenge-[number]/
    git commit -m "Add Challenge [number]: [Challenge Title]"
    
    # 对于包挑战
    git add packages/[package-name]/
    git commit -m "Add [Package] Challenge [number]: [Challenge Title]"
    
    git push origin [branch-name]
    ```

13. **创建拉取请求：**

    - 提交拉取请求以供审查。
    - 确保所有测试在CI工作流程中通过。
    - 包含挑战及其教育价值的详细描述。

---

## **风格指南**

- **代码格式化：**

  - 使用 `gofmt` 格式化您的Go代码。
  - 保持一致的缩进和间距。

- **命名约定：**

  - 使用描述性的变量和函数名称。
  - 遵循Go命名约定（例如，变量和函数使用 `camelCase`）。

- **注释：**

  - 包含注释以解释复杂逻辑。
  - 为导出的函数和类型使用文档注释（`//`）。

- **测试编写：**

  - 编写彻底的测试，涵盖各种输入情况。
  - 使用子测试（`t.Run()`）来组织测试用例。

---

## **拉取请求流程**

1. **确保所有测试通过：**

   - 在提交拉取请求之前在本地运行测试。
   - 检查您的代码不会破坏现有功能。

2. **提供清晰的描述：**

   - 解释您做了什么更改以及为什么。
   - 引用任何相关问题。

3. **每个功能一个拉取请求：**

   - 保持您的拉取请求专注于单个功能或修复。

4. **等待审查：**

   - 维护者将审查您的拉取请求。
   - 对反馈做出响应并进行必要的更改。

---

## **报告问题**

如果您遇到任何问题或有建议：

- **打开问题：**

  - 转到[问题](https://github.com/RezaSi/go-interview-practice/issues)标签。
  - 提供问题或建议的详细描述。
  - 如适用，请包含重现问题的步骤。

---

## **联系方式**

如有任何问题或需要额外支持：

- **邮箱：** [rezashiri88@gmail.com](mailto:rezashiri88@gmail.com)
- **GitHub：** [RezaSi](https://github.com/RezaSi)

---

感谢您为Go面试实战仓库做出贡献！
