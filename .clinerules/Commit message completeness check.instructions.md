---
applyTo: "**"
textId: "INST-015"
---

## Commit Message Completeness Check

Before committing any changes, you must verify that your commit message accurately covers the scope of all staged changes. This is a mandatory process check to ensure complete and accurate commit history.

### Mandatory Process

**Before writing your commit message:**

1. **Review all staged changes:** Run `git diff --cached` to see exactly what will be committed
2. **List affected areas:** Identify all files, modules, and functional areas being modified
3. **Check for scope completeness:** Ensure your commit message mentions or implies all significant changes
4. **Verify accuracy:** Confirm that the commit message doesn't claim changes that aren't actually staged

### What Makes a Complete Commit Message

A complete commit message should:

- **Cover all functional areas** affected by the staged changes
- **Mention significant file additions, deletions, or renames**
- **Describe both code and documentation changes** if both are staged
- **Include configuration or build system changes** if present
- **Reference test additions or modifications** if included

### Examples

**Incomplete (Bad):**

```
Fix tests
```

*When the commit actually includes test fixes, new helper functions, and documentation updates.*

**Complete (Good):**

```
Fix FlowBackflow tests and add missing helper functions

- Add missing process_action_with_backflow/1 helper function
- Fix Flow.with_index usage in workflow processing
- Update test documentation for clarity
```

### Red Flags - Incomplete Messages

- Generic messages like "Fix bugs" or "Update code"
- Messages that only mention one change when multiple areas are affected
- Missing mention of documentation changes when docs are staged
- Not describing the scope when multiple files/modules are modified
- Claiming changes that aren't actually in the staging area

### Rationale

- **Accurate history:** Future developers can understand what was actually changed
- **Easier debugging:** When issues arise, you know exactly what each commit changed
- **Better reviews:** Reviewers can verify the commit does what it claims
- **Proper scope tracking:** Each commit has a clear, complete scope definition

### Enforcement

This check is **mandatory** - incomplete commit messages must be rewritten before committing. Take the time to review your staged changes and write a message that completely describes the scope of work being committed.
