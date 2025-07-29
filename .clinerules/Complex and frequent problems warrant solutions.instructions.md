---
applyTo: "**"
textId: "INST-021"
---

## Complex and frequent problems warrant solutions

Solutions should be implemented only for problems that are either too complex for most users to solve themselves or occur frequently enough to become an annoyance.

### The principle

Not every problem needs a built-in solution. The software should solve problems based on two criteria: complexity (too difficult for users to handle) and frequency (occurs often enough to be annoying).

### Decision matrix

**Implement a solution when:**

- **High complexity + Any frequency:** Problem is too complex for most users to solve
- **Low complexity + High frequency:** Problem is simple but users encounter it repeatedly

**Don't implement a solution when:**

- **Low complexity + Low frequency:** Users can easily work around it occasionally

### Assessing complexity

**High complexity indicators:**

- Requires deep technical knowledge
- Involves multiple systems or components
- Has non-obvious edge cases or failure modes
- Requires significant debugging or troubleshooting skills

**Low complexity indicators:**

- Can be solved with a few lines of code
- Has a clear, documented workaround
- Follows obvious patterns users already know

### Assessing frequency

**High frequency indicators:**

- Users encounter this in most projects
- The workaround needs to be repeated regularly
- Multiple users report the same problem
- The issue blocks common workflows

**Low frequency indicators:**

- Only affects edge cases or unusual setups
- Rarely reported by users
- Specific to particular use cases or configurations

### Examples

**Should solve (high complexity):**

- Cryptographic implementations
- Complex algorithms (pathfinding, physics)
- Platform-specific integration issues
- Performance-critical operations

**Should solve (high frequency):**

- Common data transformations
- Frequent validation patterns
- Standard configuration setups
- Repetitive boilerplate code

**Should not solve:**

- One-off utility functions
- Project-specific customizations
- Rare edge case handling
- Simple data manipulations

### Implementation guidelines

When implementing solutions for complex/frequent problems:

- **Keep the common case simple:** Make the most frequent usage pattern easy
- **Document thoroughly:** Complex solutions need clear documentation
- **Provide examples:** Show users how to handle typical scenarios
- **Consider edge cases:** Complex problems often have non-obvious edge cases

This principle ensures development effort is focused on problems that genuinely benefit from built-in solutions.
