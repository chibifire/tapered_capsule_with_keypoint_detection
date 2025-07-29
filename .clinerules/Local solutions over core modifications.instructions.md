---
applyTo: "**"
textId: "INST-019"
---

## Local solutions over core modifications

When solving problems, prefer implementing solutions close to where the problem occurs rather than adding complexity to core systems or shared modules.

### The principle

Keep solution code as close as possible to where the problem originates, even if this means writing more code, duplicating some logic, or creating less efficient implementations.

### Why this matters

- **Cleaner core systems:** Keeps foundational code simple and focused
- **Easier to understand:** Problem and solution are located near each other
- **Reduced coupling:** Changes don't ripple through multiple systems
- **Better maintainability:** Each area of code handles its own concerns

### What to avoid

- **Core system pollution:** Adding specialized functionality to shared modules
- **Distant solutions:** Solving problems far from where they occur
- **Quick hacks in foundational code:** Taking shortcuts that affect system-wide stability
- **Premature abstraction:** Moving code to shared locations before patterns are clear

### Implementation approach

1. **Identify the problem location:** Find where the issue actually occurs
2. **Look for local solutions first:** Can this be solved in the same module or nearby?
3. **Accept some duplication:** It's better to have clear, local code than complex shared code
4. **Only abstract when patterns emerge:** Move to shared code only after seeing repeated need

### Examples

**Good (local solution):**

```
# In the module where validation is needed
def validate_user_input(input)
  return false if input.nil? || input.empty?
  return false if input.length > MAX_LENGTH
  true
end
```

**Avoid (core modification):**

```
# Adding specialized validation to a shared utility module
# that only one area of code actually needs
```

### When to make exceptions

Consider core modifications only when:

- Multiple unrelated modules need identical functionality
- The solution truly belongs in the core domain
- Performance requirements make local solutions impractical
- A clear, well-established pattern has emerged

### Benefits

- **Clearer code organization:** Related functionality stays together
- **Easier debugging:** Problems and solutions are co-located
- **Safer refactoring:** Changes have limited scope of impact
- **Better newcomer experience:** Core systems remain approachable

This principle helps maintain clean architectural boundaries and makes codebases easier to understand and maintain.
