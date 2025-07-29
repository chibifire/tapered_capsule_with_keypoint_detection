---
applyTo: "**"
textId: "INST-014"
---

## Commit message style

Use descriptive, complete commit messages that communicate the full scope of changes with natural language. This project intentionally avoids "conventional commit" style prefixes in favor of clear, complete descriptions.

### Critical Rule

**Absolutely no conventional commit prefixes (e.g., `feat:`, `fix:`, `docs:`, `refactor:`, etc.) are allowed.** Commit messages must start directly with a descriptive, natural language sentence.

### Style Guidelines

**Preferred approach:**

- Write complete sentences that describe what was accomplished
- Include context about why changes were made when relevant
- Reference ADRs, issues, or architectural decisions when applicable
- Use natural, professional language with Aria's supportive personality

**Avoid conventional commit style:**

- Do not use prefixes like `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Do not use scope notation like `feat(auth):` or `fix(engine):`
- These formats are too rigid and don't capture the complete context needed for this project

Follow the completeness check process before every commit to ensure your message accurately describes the full scope of changes being committed.
