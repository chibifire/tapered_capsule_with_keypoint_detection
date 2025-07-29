---
applyTo: "**"
textId: "INST-026"
---

## Update ADR progress documentation

When working on any task defined in an Architecture Decision Record (ADR), you must update the ADR document to reflect progress made during each work session.

### The principle

ADRs serve as living documentation of active work. They must be kept current to accurately reflect the state of implementation and provide clear tracking for future development sessions.

### When to update ADRs

**Update required after:**

- **Completing any task:** Mark completed tasks with `- [x]` checkbox syntax
- **Making significant progress:** Add progress notes for partially completed tasks
- **Encountering blockers:** Document obstacles and their resolution status
- **Changing implementation approach:** Update the decision or implementation plan sections
- **Adding new discoveries:** Include relevant findings that affect the work

### What to update

**Task completion:**

```markdown
- [x] Complete AriaFlow core API implementation
  - ✅ Extracted features from backup file
  - ✅ Fixed type compatibility issues
  - ✅ All tests passing (7 tests, 0 failures)
```

**Progress notes:**

```markdown
- [ ] Integrate with aria_engine workflow system
  - 🔄 In progress: Basic integration structure created
  - 📝 Next: Implement workflow event handlers
```

**Status updates:**

```markdown
**Status:** Active → Completed (June 15, 2025)
```

### Implementation approach

1. **Before starting work:** Review the current ADR to understand scope and status
2. **During work sessions:** Take notes of progress and decisions made
3. **After completing tasks:** Update the ADR with completed checkboxes and results
4. **When committing code:** Include ADR updates in the same commit when relevant
5. **When encountering changes:** Update implementation plans to reflect new understanding

### Required sections to maintain

**Always keep current:**

- **Status field:** Proposed → Active → Completed
- **Task checkboxes:** Accurate completion state
- **Implementation Plan:** Reflects current approach and remaining work
- **Success Criteria:** Updated if criteria change during implementation

**Add when relevant:**

- **Progress Notes:** Detailed updates on partially completed work
- **Lessons Learned:** Important discoveries made during implementation
- **Completion Date:** When ADR reaches "Completed" status

### Benefits

- **Accurate tracking:** Clear understanding of what work has been completed
- **Continuity:** Future work sessions can pick up where previous sessions left off
- **Documentation:** Maintains historical record of implementation decisions
- **Team coordination:** Other developers can see current progress and status
- **Accountability:** Ensures work is properly documented and tracked

### What to avoid

- **Stale ADRs:** Leaving ADRs with outdated task states or progress information
- **Generic updates:** Vague progress notes that don't provide useful information
- **Forgetting status changes:** Not updating the overall ADR status when work is complete
- **Missing context:** Updates without sufficient detail for future reference

This requirement ensures that ADRs remain valuable, current documentation throughout the development process.
