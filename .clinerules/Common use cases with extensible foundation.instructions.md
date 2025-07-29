---
applyTo: "**"
textId: "INST-018"
---

## Common use cases with extensible foundation

Design solutions that handle common use cases elegantly while providing low-level access for rare or complex scenarios. This balances usability with flexibility.

### The principle

Create simple, focused solutions for the most common use cases (80% scenarios) while ensuring that underlying systems remain accessible for users who need to handle edge cases or complex requirements.

### Implementation approach

1. **Identify the common case:** Determine what most users need to accomplish
2. **Design for simplicity:** Make the common case as simple as possible to use
3. **Preserve low-level access:** Ensure advanced users can access underlying functionality
4. **Document both paths:** Clearly explain the simple path and the advanced alternatives

### What this looks like in practice

**For code:**

- Provide simple helper functions for common operations
- Keep the underlying detailed functions available
- Offer sensible defaults while allowing customization

**For instruction files:**

- Focus each instruction on one common scenario or rule
- Reference related instructions for edge cases
- Keep explanations clear and actionable

### Example structure

```
High-level API (common case):
  - Simple function calls
  - Sensible defaults
  - Clear documentation

Low-level API (rare cases):
  - Direct access to underlying systems
  - Full customization options
  - Advanced documentation
```

### Benefits

- **Easy adoption:** New users can accomplish common tasks quickly
- **Maintains power:** Advanced users aren't limited by simplified interfaces
- **Reduces support burden:** Most users can solve their problems with the simple path
- **Future flexibility:** Edge cases can be handled without redesigning the core system

### What to avoid

- **Over-complicating the common case:** Don't make simple tasks require complex setup
- **Hiding necessary functionality:** Ensure advanced features remain accessible
- **Poor documentation:** Both simple and advanced paths need clear guidance

This approach ensures that the majority of users have a smooth experience while maintaining the flexibility needed for complex scenarios.
