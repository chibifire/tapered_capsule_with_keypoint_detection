---
applyTo: "**"
textId: "INST-017"
---

## Targeted solutions over generalized systems

Each problem should receive its own focused solution rather than trying to create one system that solves multiple unrelated problems. This principle promotes code clarity and maintainability.

### The principle

Design individual solutions for individual problems instead of attempting to create overly flexible systems that handle multiple use cases. **Each instruction file and each code module should have a single, well-defined responsibility.**

### Why this matters

- **Simpler code:** Individual solutions are easier to understand and maintain
- **Better user experience:** Users can find exactly what they need without learning complex systems
- **Reduced complexity:** Avoids the pitfall of over-engineering solutions
- **Clearer separation of concerns:** Each solution has a clear, single purpose

### What to avoid

- **Swiss army knife solutions:** Systems that try to solve many different problems
- **Over-generalization:** Creating flexible frameworks when simple solutions would suffice
- **Feature creep:** Adding functionality beyond the original problem scope
- **Speculation-based flexibility:** Adding features for problems that don't currently exist

### Implementation approach

1. **Identify the specific problem:** Focus on one clear, well-defined issue
2. **Design a targeted solution:** Create the simplest implementation that solves this problem
3. **Resist feature expansion:** Keep the solution focused on the original problem
4. **Document the single purpose:** Clearly state what the solution does and doesn't do

### Single responsibility emphasis

**This principle applies especially to instruction files and code modules.** Each should have one clear purpose:

- **Instruction files:** One rule, process, or guideline per file
- **Code modules:** One logical unit of functionality per module
- **Functions:** One clear task per function
- **Classes:** One clear responsibility per class

### Benefits

- **Easier debugging:** When something breaks, you know exactly which solution to examine
- **Simpler testing:** Each solution can be tested independently
- **Better maintenance:** Changes to one solution don't affect others
- **Clearer documentation:** Each solution can be documented completely and clearly

This approach leads to cleaner, more maintainable codebases where each component has a clear, single purpose.
