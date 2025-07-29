---
applyTo: "**"
textId: "INST-024"
---

## Extract tasks into dedicated ADRs

When a task within an existing ADR becomes complex enough to warrant independent tracking and implementation, extract it into its own dedicated ADR with proper cross-references.

### The principle

Large, complex tasks within broader ADRs should be extracted into focused, independent ADRs to enable better tracking, implementation planning, and completion verification.

### When to extract tasks

**Extract when a task has:**

- **Independent implementation scope:** Can be worked on separately from other tasks
- **Significant complexity:** Requires detailed planning, multiple steps, or specialized knowledge
- **Clear completion criteria:** Has measurable success conditions distinct from the parent ADR
- **Blocking priority:** Is critical path work that needs focused attention
- **Multiple sub-tasks:** Contains several related implementation steps

### Implementation approach

1. **Create the new ADR:**
   - Use the next available ADR number
   - Include detailed context from the original task
   - Expand task details into full implementation plan
   - Add success criteria and monitoring approach
   - Reference the parent ADR and related ADRs

2. **Update the original ADR:**
   - Cross out the extracted task using `~~strikethrough~~` formatting
   - Add reference to new ADR with arrow notation: `→ Moved to ADR-XXX`
   - Update any affected progress tracking sections
   - Add the new ADR to Related ADRs section

3. **Commit the changes:**
   - Stage both the new ADR and updated original ADR
   - Write complete commit message covering both files
   - Explain the extraction rationale and cross-references

### What the extracted ADR should include

**Essential sections:**

- **Status:** Active with clear start date and priority level
- **Context:** Detailed background from original ADR plus additional analysis
- **Implementation Plan:** Expanded task breakdown with phases and sub-tasks
- **Success Criteria:** Specific, measurable completion conditions
- **Related ADRs:** Cross-references to parent and related ADRs
- **Timeline:** Target completion and dependencies

**Additional considerations:**

- **Risks and consequences:** Specific to the extracted work
- **Monitoring:** How progress will be tracked independently
- **Prerequisites:** Dependencies that must be resolved first

### Cross-reference formatting

**In the original ADR:**

```markdown
- ~~[ ] Complex task requiring extraction~~ **→ Moved to ADR-XXX**
```

**In the extracted ADR:**

```markdown
## Related ADRs

- **ADR-YYY**: Parent ADR Name (extracted from this ADR)
- **ADR-ZZZ**: Related ADR Name
```

### Benefits

- **Focused implementation:** Each ADR addresses a single, well-defined scope
- **Better tracking:** Progress on complex tasks is independently monitored
- **Clearer priorities:** Critical tasks get dedicated attention and planning
- **Improved collaboration:** Team members can work on specific ADRs independently
- **Maintainable documentation:** Each ADR remains focused and manageable

### What to avoid

- **Over-extraction:** Don't create separate ADRs for simple, quick tasks
- **Broken references:** Ensure all cross-references are accurate and bidirectional
- **Incomplete context:** The extracted ADR must have sufficient background to stand alone
- **Orphaned tasks:** Don't extract without proper cross-referencing

### Example workflow

1. **Identify extraction candidate:** "BaselineTest failures in aria_timestrike (4 failures)"
2. **Create ADR-058:** Detailed context, implementation plan, success criteria
3. **Update parent ADR-057:** Cross out task, add reference arrow, update Related ADRs
4. **Commit together:** Both changes in single commit with complete message
5. **Work independently:** ADR-058 can now be implemented without affecting ADR-057

This pattern maintains clear traceability while enabling focused work on complex tasks that deserve dedicated attention and planning.
