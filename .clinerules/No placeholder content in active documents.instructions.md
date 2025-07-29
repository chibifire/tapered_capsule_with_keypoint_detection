---
applyTo: "**"
textId: "INST-029"
---

## No placeholder content in active documents

Never add placeholder links, template text, or example content to active ADRs, documentation, or code files. Placeholder content pollutes documents and creates confusion about what is real versus what needs to be filled in.

### The principle

Active documents should only contain real, actionable content. Placeholders belong in templates, examples, or draft documents—never in working project files.

### What constitutes placeholder content

**Prohibited placeholder examples:**

- `[Your research links here]`
- `TODO: Add implementation details`
- `Example: https://example.com/placeholder-link`
- `<!-- TODO: Fill this section -->`
- Incomplete sections with "TBD" or "Coming soon"
- Template boilerplate left in active documents

### When placeholders are acceptable

**Only in these contexts:**

- **Template files:** Explicitly labeled as templates for creating new documents
- **Example files:** Clear examples showing document structure
- **Draft documents:** Clearly marked as work-in-progress with draft status
- **Code comments:** Legitimate TODO comments for future implementation

### Correct approach instead

**When you need to add structure for future content:**

1. **Ask for the actual content:** "Could you provide the research links you'd like me to add?"
2. **Create empty but labeled sections:** Use clear headings but leave content areas empty
3. **Document the need:** "Research section ready for your interval notation findings"
4. **Use draft status:** Mark documents as drafts if they're incomplete

### Implementation examples

**Bad (placeholder pollution):**

```markdown
## Research and References

### Research Links
- [Add your interval notation research here]
- [Placeholder for additional resources]

### Key Findings
- TODO: Document important discoveries
```

**Good (clean structure):**

```markdown
## Research and References

*Research section ready for interval notation findings and references.*
```

**Better (specific request):**

```markdown
I've identified that ADR-045 covers Allen's Interval Algebra.
Would you like me to add a research section where you can
document your interval notation research findings?
```

### Why this matters

- **Document integrity:** Active documents remain trustworthy and actionable
- **Reduced confusion:** Readers can distinguish real content from placeholders
- **Better maintenance:** No cleanup needed to remove placeholder content
- **Professional appearance:** Documents look complete and authoritative

### Red flags

- Adding sections with placeholder text "to be helpful"
- Including template examples in production documents
- Creating TODOs for content that should be provided immediately
- Assuming what content someone wants to add

This follows the problem-first approach—the problem is document pollution, and the solution is only adding real content to active documents.
