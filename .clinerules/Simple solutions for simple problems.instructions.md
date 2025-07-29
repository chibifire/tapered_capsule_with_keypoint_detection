---
applyTo: "**"
textId: "INST-022"
---

## Simple solutions for simple problems

Avoid using complex third-party libraries or over-engineered solutions when the problem can be solved with simple, straightforward code.

### The principle

Match the complexity of your solution to the complexity of the problem. Simple problems should receive simple solutions, even if more sophisticated alternatives exist.

### When to use simple solutions

- **The problem has a clear, straightforward solution**
- **The required functionality is limited in scope**
- **A few lines of custom code can solve the problem**
- **The problem doesn't require specialized expertise**
- **Performance requirements are reasonable**

### What constitutes a simple solution

- **Minimal dependencies:** Uses only necessary external libraries
- **Clear implementation:** Code is easy to read and understand
- **Limited scope:** Solves exactly the problem at hand
- **Standard patterns:** Uses well-known approaches and conventions

### When to consider complex solutions

Use more sophisticated approaches only when:

- **Problem complexity genuinely warrants it:** The domain is inherently complex
- **Specialized knowledge is required:** Cryptography, algorithms, platform-specific code
- **Performance is critical:** Optimizations require specialized implementations
- **Maintenance burden is high:** Well-tested libraries reduce long-term costs

### Third-party library considerations

**Prefer libraries that are:**

- **Small and focused:** Single-purpose libraries with minimal footprint
- **Well-maintained:** Active development and good track record
- **Permissively licensed:** Compatible with project licensing requirements
- **Minimal dependencies:** Don't bring in large dependency trees

**Avoid libraries that:**

- **Solve simple problems:** When custom code would be clearer
- **Are overly complex:** Bring unnecessary complexity for your use case
- **Have restrictive licenses:** Conflict with project requirements
- **Are poorly maintained:** Inactive development or known issues

### Implementation approach

1. **Assess problem complexity:** Is this genuinely complex or just unfamiliar?
2. **Consider custom implementation:** Can this be solved in a reasonable amount of code?
3. **Evaluate alternatives:** Compare simple custom code vs. library solutions
4. **Choose the appropriate tool:** Match solution complexity to problem complexity

### Benefits of simple solutions

- **Easier maintenance:** Less code to maintain and debug
- **Better understanding:** Team members can easily understand and modify the code
- **Fewer dependencies:** Reduced risk from external library changes
- **Faster development:** No need to learn complex APIs for simple problems

### Examples

**Good (simple solution):**

```
# For basic string manipulation
def slugify(text)
  text.downcase.gsub(/[^a-z0-9]+/, '-').strip('-')
end
```

**Avoid (over-engineered):**

```
# Including a large text processing library
# just for basic string operations
```

This principle helps maintain clean, understandable codebases by matching solution complexity to problem complexity.
