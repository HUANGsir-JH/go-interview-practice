# Learn to Reverse a String

## String Operations in Go

This challenge focuses on string handling in Go, particularly string reversal. Understanding how Go represents and manipulates strings is crucial for this task.

### Strings in Go

In Go, strings are immutable sequences of bytes. They are typically used to represent text and are encoded in UTF-8 by default. String literals can be created using double quotes or backticks:

```go
// Using double quotes
s1 := "Hello, world"

// Using backticks to create raw strings (preserve newlines and escape characters)
s2 := `Line 1
Line 2`
```

### Runes and Bytes

When working with strings in Go, it's important to understand the difference between bytes and runes:

- **Bytes**: Single 8-bit units (uint8), representing individual ASCII characters or parts of UTF-8 encoded characters
- **Runes**: Individual Unicode code points (int32), capable of representing any character

For ASCII strings, bytes and runes are essentially the same. However, for strings containing non-ASCII characters (such as emojis, accented characters, or non-Latin scripts), treating strings as byte sequences may lead to incorrect results.

```go
s := "Hello, 世界"
fmt.Println(len(s))        // Output: 13 (number of bytes)
fmt.Println(utf8.RuneCountInString(s))  // Output: 9 (number of characters)
```

### String Reversal Strategies

When reversing strings in Go, several approaches should be considered:

1. **Byte-by-byte reversal**: Simple, but may break UTF-8 encoding of non-ASCII characters
2. **Rune-by-rune reversal**: Preserves UTF-8 encoding and correctly handles all characters

### String Conversion and Slicing

Converting between strings, runes, and bytes is common in Go:

```go
s := "Hello"
runeSlice := []rune(s)    // Convert string to rune slice
byteSlice := []byte(s)    // Convert string to byte slice
s1 := string(runeSlice)   // Convert rune slice back to string
s2 := string(byteSlice)   // Convert byte slice back to string
```

### Iteration Techniques

Go provides several ways to iterate over strings:

```go
// Iterate byte by byte (be careful with Unicode!)
s := "Hello"
for i := 0; i < len(s); i++ {
    fmt.Printf("%c ", s[i])
}

// Iterate rune by rune (safer for Unicode)
for _, r := range s {
    fmt.Printf("%c ", r)
}

// Use explicit conversion to runes
runes := []rune(s)
for i := 0; i < len(runes); i++ {
    fmt.Printf("%c ", runes[i])
}
```

### Key Concepts for String Reversal

- **Two-pointer technique**: A common algorithmic pattern for reversing sequences
- **Slice operations**: Understanding how to work with rune or byte slices
- **Unicode considerations**: Ensuring your solution correctly handles non-ASCII characters
- **String immutability**: Strings cannot be modified in place, so a new string must be created

### Common String Operations

The `strings` package provides many functions for string manipulation:

```go
import "strings"

s := "Hello, World!"
fmt.Println(strings.Contains(s, "World"))  // true
fmt.Println(strings.ToUpper(s))            // HELLO, WORLD!
fmt.Println(strings.ToLower(s))            // hello, world!
fmt.Println(strings.Replace(s, "Hello", "Hi", 1)) // Hi, World!
fmt.Println(strings.Split(s, ", "))        // ["Hello", "World!"]
```

## Further Reading

- [Go by Example: Strings and Runes](https://gobyexample.com/string-functions)
- [Strings, Bytes, Runes, and Characters in Go](https://blog.golang.org/strings)
- [Unicode Support in Go](https://blog.golang.org/normalization)