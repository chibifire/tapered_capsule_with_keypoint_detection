---
applyTo: "**"
textId: "INST-010"
---

## Update design change logs

When notable changes are made to the system's design, update the relevant ADR with a "Change Log" section to maintain accurate documentation.

### The principle

Design changes should be documented immediately in the corresponding ADR to ensure the documentation remains current and accurately reflects the state of the codebase.

### Implementation approach

1. **Identify the affected ADR:** Determine which Architecture Decision Record covers the area being changed
2. **Add or update Change Log section:** Create a "Change Log" section if it doesn't exist, or add a new entry
3. **Document the change:** Add an entry with date, description of what was changed, and rationale
4. **Include relevant details:** Add context that will help future developers understand the evolution
5. **Commit with the change:** Include ADR updates in the same commit as the design change

### Change Log format

```markdown
## Change Log

### June 15, 2025
- Updated API interface to support new validation patterns
- Reason: Enhanced error handling requirements from user feedback

### June 10, 2025  
- Modified core workflow processing logic
- Reason: Performance optimization based on load testing results
```

### Benefits

- **Historical context:** Maintains a clear record of design evolution
- **Better understanding:** Helps current and future developers understand decisions
- **Reduced confusion:** Prevents questions about why certain design choices were made
- **Documentation consistency:** Keeps documentation in sync with actual implementation

This practice follows the problem-first approach - the problem is losing track of design decisions, and the solution is immediate documentation.
