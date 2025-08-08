# Bank Account Learning Materials (with Error Handling)

## Error Handling in Go

Error handling is a crucial aspect of writing robust Go programs. This challenge focuses on implementing a banking system with proper error handling techniques.

### Basic Error Handling

Go uses return values for explicit error handling, rather than exceptions:

```go
// Function that may return an error
func divideNumbers(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Handle errors using if checks
result, err := divideNumbers(10, 0)
if err != nil {
    fmt.Println("Error:", err)
    return // or handle the error
}
fmt.Println("Result:", result)
```

### Creating Custom Errors

Standard ways to create errors:

```go
// Use errors.New for simple error messages
err := errors.New("insufficient funds")

// Use fmt.Errorf for formatted error messages
amount := 100
err := fmt.Errorf("insufficient funds: need $%d more", amount)
```

### Custom Error Types

Creating custom error types enables more detailed error handling:

```go
// Define a custom error type
type InsufficientFundsError struct {
    Balance float64
    Amount  float64
}

// Implement the error interface
func (e *InsufficientFundsError) Error() string {
    return fmt.Sprintf("insufficient funds: current balance $%.2f, attempted withdrawal $%.2f",
        e.Balance, e.Amount)
}
```

**Key concepts for custom errors:**
- Implement `Error() string` method
- Include relevant context in error fields
- Use pointer receivers when checking error types
- Use `ok` pattern for type assertions to check error types

### Error Wrapping (Go 1.13+)

Go 1.13 introduced error wrapping to provide better error context:

**Key concepts:**
- Use `fmt.Errorf` with `%w` placeholder to wrap errors
- Use `errors.As()` to check for specific error types in error chains
- Use `errors.Is()` to check for specific error values in error chains
- Preserve original error context while adding meaningful information

### Sentinel Errors

Predefined errors that can be directly compared:

```go
// Define sentinel errors as package-level variables
var (
    ErrAccountNotFound   = errors.New("account not found")
    ErrInsufficientFunds = errors.New("insufficient funds")
    ErrInvalidAmount     = errors.New("invalid amount")
)
```

**Key concepts:**
- Define reusable errors using package-level variables
- Compare errors using `==` or `errors.Is()`
- Provide clear, descriptive error messages

### Error Handling Patterns

#### 1. Early Return Pattern
Validate inputs first and return errors immediately, avoiding deep nesting.

#### 2. Error Handler Functions
Create functions that process multiple error-prone operations in sequence.

#### 3. Error Context
Always provide meaningful context when returning or wrapping errors.

### Special Considerations for Banking Applications

#### Account Operations
- **Balance Validation**: Check sufficient balance before withdrawal
- **Amount Validation**: Ensure deposit/withdrawal amounts are positive
- **Account Existence Validation**: Confirm account exists before operation
- **Input Sanitization**: Validate all user inputs

#### Banking-Specific Error Types
- **InsufficientFundsError**: Specific error for balance issues
- **InvalidAmountError**: For negative or zero amounts
- **AccountNotFoundError**: Used when account lookup fails
- **ValidationError**: Used when input validation fails

### Thread Safety in Banking Applications

Banking applications must handle concurrent access:

**Key concepts:**
- Use `sync.Mutex` to protect account operations
- Lock before checking balance and modifying it
- Use `defer` to ensure mutex is always released
- Consider read-write locks for read-heavy, write-light operations

### Testing Error Scenarios

Testing error handling is critical:

**Testing strategies:**
- Test each error case separately
- Verify error types and messages
- Test successful operations after handling errors
- Use table-driven tests for multiple error scenarios
- Mock dependencies to simulate error conditions

### Logging and Reporting Errors

Proper error logging is essential:

**Best practices for logging:**
- Include sufficient context when logging errors
- Include relevant identifiers (account, transaction, user)
- Log at appropriate levels (error, warning, info)
- Avoid duplicating error logs in call stack
- Use structured logging for easier parsing and monitoring

### Panic and Recover

Although Go favors explicit error handling, `panic` and `recover` are still useful in special cases:

**When to use panic:**
- Unrecoverable errors indicating programmer mistakes
- Initialization failures preventing program execution
- Internal consistency violations

**Recovery patterns:**
- Use `defer` with `recover()` to catch panics
- Convert panics to errors when appropriate
- Log panics for debugging
- Only recover at appropriate boundaries

## Further Reading

- [Error Handling in Go](https://blog.golang.org/error-handling-and-go)
- [Error Handling in Go 1.13+](https://blog.golang.org/go1.13-errors)
- [Effective Error Handling in Go](https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully)
- [Sync Package Documentation](https://pkg.go.dev/sync)