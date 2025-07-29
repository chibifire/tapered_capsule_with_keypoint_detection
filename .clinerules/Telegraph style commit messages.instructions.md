---
applyTo: "**"
textId: "INST-039"
---

## Telegraph style commit messages

Write commit messages using telegraph-style economy of words while maintaining proper sentence case and technical clarity. Ensure a secondary summary line.

### The principle

Like telegraph messages where every word costs money, strip all unnecessary words while preserving essential technical information. Focus on what was done to which component with maximum efficiency.

### Telegraph-style guidelines

**Word economy rules:**

- **Remove articles:** Eliminate "a", "an", "the" unless critical for clarity
- **Strip filler words:** Remove "to", "in order to", "that", "which", "some", "various"
- **Eliminate redundancy:** Avoid phrases like "in the system" or "of the application"
- **Use direct action:** Lead with verbs (Fix, Add, Update, Refactor, Remove)
- **Essential information only:** What was done, to what component, why if critical

**Maintain readability:**

- **Proper sentence case:** Start with capital letter, normal capitalization throughout
- **Technical precision:** Never sacrifice clarity for brevity
- **Component identification:** Clearly name the affected module or system
- **Action clarity:** Ensure the change type is obvious

### Implementation examples

**Before (verbose):**

```
Fix the critical bug that was occurring in the hybrid coordinator initialization process
Add comprehensive test coverage for the workflow validation system
Refactor the strategy factory to improve the modularity of the codebase
Update the documentation for the planning system components
Remove deprecated functions from the legacy authentication module
```

**After (telegraph style):**

```
Fix coordinator init bug
Add workflow validation tests
Refactor strategy factory modularity
Update planning docs
Remove deprecated auth functions
```

### Advanced telegraph patterns

**Multiple components:**

- Instead of: "Update tests and documentation for coordinator"
- Telegraph: "Update coordinator tests and docs"

**Bug fixes with context:**

- Instead of: "Fix memory leak in planning execution"
- Telegraph: "Fix planning execution memory leak"

**Feature additions:**

- Instead of: "Add new validation logic for workflow states"
- Telegraph: "Add workflow state validation"

### Integration with existing rules

This telegraph style works alongside:

- **Commit message completeness:** Still must cover full scope of changes
- **Professional language:** Maintains technical terminology and proper case
- **Emoji distribution:** Can include emojis following Zipfian patterns
- **Natural language requirement:** Avoids conventional commit prefixes

### Benefits

- **Faster reading:** Essential information immediately visible
- **Cleaner git logs:** More commits visible in standard terminal views
- **Focused communication:** Forces identification of core changes
- **Historical telegraph aesthetic:** Efficient communication style with character

### What to avoid

- **Sacrificing clarity:** Never make messages unclear for brevity
- **Over-abbreviation:** Avoid cryptic shortened words
- **Missing context:** Include enough detail for future understanding
- **Removing technical terms:** Keep precise component and action names

This approach creates commit messages that respect the telegraph tradition of maximum information with minimum words while maintaining professional development communication standards.
