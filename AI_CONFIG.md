# AI配置用于实时代码审查

## 设置说明

### 1. 环境变量

在项目根目录创建一个`.env`文件或设置这些环境变量：

```bash
# 设置您首选的AI提供商：gemini、openai、claude或mock
export AI_PROVIDER=gemini

# API密钥（只设置您正在使用的那个）
export GEMINI_API_KEY=your_gemini_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
export CLAUDE_API_KEY=your_claude_api_key_here

# 可选：覆盖默认模型
export AI_MODEL=gemini-pro
```

### 2. 获取API密钥

#### Gemini（推荐 - 提供免费层级）
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 设置 `AI_PROVIDER=gemini` 和 `GEMINI_API_KEY=your_key`

#### OpenAI
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 创建新的API密钥
3. 设置 `AI_PROVIDER=openai` 和 `OPENAI_API_KEY=your_key`

#### Claude
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 创建新的API密钥
3. 设置 `AI_PROVIDER=claude` 和 `CLAUDE_API_KEY=your_key`

### 3. 开发模式

在没有API密钥的情况下进行测试，使用模拟AI：
```bash
export AI_PROVIDER=mock
```

这提供了逼真的响应，而无需进行外部API调用。

### 4. 启动服务器

```bash
cd web-ui
go run main.go
```

AI功能将在以下位置可用：
- `POST /api/ai/code-review` - 实时代码分析
- `POST /api/ai/interviewer-questions` - 生成后续问题
- `POST /api/ai/code-hint` - 上下文感知提示

## 功能 ✅ 正常工作

### 实时代码审核 ✅
- **总体评分**：0-100的代码质量评分
- **问题检测**：错误、性能、风格、逻辑问题
- **建议**：优化和最佳实践推荐
- **复杂度分析**：时间/空间复杂度评估
- **面试官反馈**：真实面试官会说的话
- **安全性**：所有内容都经过HTML转义以确保安全

### 动态面试问题 ✅
- 基于用户解决方案的上下文感知问题
- 基于用户表现的渐进难度
- Go特定的技术探索
- 边界情况探索
- 每次请求5个相关问题数组

### 智能提示系统 ✅
- 4个级别的提示（微妙提示 → 详细解释）
- 基于当前代码的上下文感知
- 教授概念的教育方法
- 渐进式提示按钮（Lv1 → Lv2 → Lv3 → Lv4）

## API示例

### 代码审核
```javascript
POST /api/ai/code-review
{
  "challengeId": 1,
  "code": "func Sum(a, b int) int { return a + b }",
  "context": "面试开始5分钟前"
}
```

### 获取面试问题
```javascript
POST /api/ai/interviewer-questions
{
  "challengeId": 1, 
  "code": "func Sum(a, b int) int { return a + b }",
  "userProgress": "完成基础解决方案"
}
```

### 获取提示
```javascript
POST /api/ai/code-hint
{
  "challengeId": 1,
  "code": "func Sum(a, b int) int { // 卡在这里 }",
  "hintLevel": 2
}
```