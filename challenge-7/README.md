[查看排行榜](SCOREBOARD.md)

# 挑战 7：带错误处理的银行账户

## 问题描述

实现一个简单的银行系统，并具备适当的错误处理。你需要创建一个 `BankAccount` 结构体来管理余额操作并实现合适的错误处理。

## 要求

1. 实现一个 `BankAccount` 结构体，包含以下字段：
   - `ID`（字符串）：账户的唯一标识符
   - `Owner`（字符串）：账户所有者姓名
   - `Balance`（float64）：账户当前余额
   - `MinBalance`（float64）：必须维持的最低余额

2. 实现以下方法：
   - `NewBankAccount(id, owner string, initialBalance, minBalance float64) (*BankAccount, error)`：构造函数，用于验证输入参数
   - `Deposit(amount float64) error`：向账户存入资金
   - `Withdraw(amount float64) error`：从账户取出资金
   - `Transfer(amount float64, target *BankAccount) error`：将资金从一个账户转账到另一个账户

3. 必须实现自定义错误类型：
   - `InsufficientFundsError`：当取款/转账会导致余额低于最低限额时抛出
   - `NegativeAmountError`：当存款/取款/转账金额为负数时抛出
   - `ExceedsLimitError`：当存款/取款金额超过你设定的限制时抛出
   - `AccountError`：通用银行账户错误，包含适当的子类型

## 函数签名

```go
// 构造函数
func NewBankAccount(id, owner string, initialBalance, minBalance float64) (*BankAccount, error)

// 方法
func (a *BankAccount) Deposit(amount float64) error
func (a *BankAccount) Withdraw(amount float64) error
func (a *BankAccount) Transfer(amount float64, target *BankAccount) error

// 错误类型
type AccountError struct {
    // 实现带有适当字段的自定义错误类型
}

type InsufficientFundsError struct {
    // 实现带有适当字段的自定义错误类型
}

type NegativeAmountError struct {
    // 实现带有适当字段的自定义错误类型
}

type ExceedsLimitError struct {
    // 实现带有适当字段的自定义错误类型
}

// 每个错误类型都应实现 Error() string 方法
func (e *AccountError) Error() string
func (e *InsufficientFundsError) Error() string
func (e *NegativeAmountError) Error() string
func (e *ExceedsLimitError) Error() string
```

## 约束条件

- 所有金额必须是有效值（非负数）。
- 取款/转账不能使账户余额低于最低余额。
- 定义合理的存款和取款限额（例如，$10,000）。
- 错误信息应具有描述性，并包含相关信息。
- 所有操作必须是线程安全的（使用适当的同步机制）。

## 示例用法

```go
// 创建新的银行账户
account1, err := NewBankAccount("ACC001", "Alice", 1000.0, 100.0)
if err != nil {
    // 处理错误
}

account2, err := NewBankAccount("ACC002", "Bob", 500.0, 50.0) 
if err != nil {
    // 处理错误
}

// 存款
if err := account1.Deposit(200.0); err != nil {
    // 处理错误
}

// 取款
if err := account1.Withdraw(50.0); err != nil {
    // 处理错误
}

// 转账
if err := account1.Transfer(300.0, account2); err != nil {
    // 处理错误
}
```

## 指导说明

- **Fork** 该仓库。
- **Clone** 你的副本到本地机器。
- 在 `challenge-7/submissions/` 目录下创建一个以你的 GitHub 用户名命名的文件夹。
- 将 `solution-template.go` 文件复制到你的提交目录中。
- **实现** 所需的结构体和方法。
- **本地测试** 你的解决方案，运行测试文件。
- **Commit** 并 **push** 代码到你的副本。
- **创建** 一个拉取请求以提交你的解决方案。

## 本地测试你的解决方案

在 `challenge-7/` 目录下运行以下命令：

```bash
go test -v
```