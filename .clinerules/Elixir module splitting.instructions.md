---
applyTo: "**"
textId: "INST-036"
---

## Elixir module splitting

When a code file becomes too large, it should be split into smaller, more manageable logical units that each serve a specific purpose.

### When to split

- Modules exceeding 200-300 lines
- Multiple distinct responsibilities
- High cognitive load
- Frequent changes in unrelated areas

### How to split

1. **Back up or disable the original file:**
   - **Backing up**: Rename with `.bak` extension (already in `.gitignore`) for complete replacement
   - **Disabling**: Rename with `.disabled` extension to preserve for reference
2. **Identify logical units** and create stubs with type annotations
3. **Create new files** for each logical unit  
4. **Update the original file** to reference the new files
5. **Test the changes** to ensure everything works as expected
6. **Remove or finalize the original file** based on your backup choice
7. **Commit the changes** with a descriptive message
8. **Verify the changes** by testing and compiling again
9. **Document the changes** in relevant documentation files
10. **Commit the documentation changes**
