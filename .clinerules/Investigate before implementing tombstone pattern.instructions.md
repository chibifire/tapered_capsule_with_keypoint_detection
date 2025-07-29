---
applyTo: "**"
textId: "INST-044"
---

# Investigate before implementing tombstone pattern

When encountering any problem that appears to require new implementation, systematically investigate whether the solution already exists and just needs proper connection or configuration.

## The principle

Many apparent "missing" problems are actually "incorrectly connected" problems. Investigate existing resources thoroughly before concluding that new implementation is required.

## Investigation methodology

**Phase 1: Map the problem scope**

1. **Define what's missing:** Clearly identify what functionality, resource, or capability appears absent
2. **Identify current attempts:** Locate where the missing item is being referenced or expected
3. **List specific requirements:** Extract the complete list of what needs to be provided

**Phase 2: Systematic existing resource exploration**

1. **Explore related areas:** Search directories, modules, configurations, and documentation that logically should contain the missing item
2. **Check alternative locations:** Examine places where the item might exist under different names or structures
3. **Verify functionality:** Confirm that discovered resources actually provide the required capabilities
4. **Map resource distribution:** Document what exists where and how it relates to the requirements

## Tombstone documentation pattern

**Update issues documentation with:**

```markdown
### X. ~~Missing [Description]~~ **TOMBSTONED ✅**

**Status:** SOLVED - [Item] exists, fix [connection/configuration/reference]

**Problem:** [System] was expecting [missing item] but couldn't find it

**Solution Found:** Required [item] exists in [location]:
- [Category A] in [Location A]
- [Category B] in [Location B]
- [Category C] in [Location C]

**Fix Required:** [Specific changes needed]:

[Concrete examples of fixes]

**Note:** [Reasoning discovered during investigation]
```

## Required tombstone elements

**Essential documentation:**

- **Clear status:** Mark as "TOMBSTONED ✅" with solved status
- **Problem description:** What was expected vs what was found
- **Solution mapping:** Where existing resources are located
- **Concrete fix:** Exact changes needed to connect existing resources
- **Investigation note:** Reasoning discovered during exploration

## Implementation validation

**Verify solution completeness:**

1. **All requirements covered:** Every missing item mapped to an existing resource
2. **Correct resource locations:** Resources actually exist and provide needed functionality
3. **Proper categorization:** Items grouped logically by their actual implementation or location
4. **Fix specificity:** Exact changes provided for connecting existing resources

## Benefits

- **Avoids duplicate implementation:** Reuses existing functionality instead of recreating it
- **Maintains system coherence:** Uses existing architectural patterns and structures
- **Provides actionable resolution:** Clear path for connecting existing resources
- **Documents discovery process:** Future developers understand why the solution wasn't obvious initially

This pattern ensures thorough investigation before concluding that new implementation is required, often revealing that the issue is connectivity rather than absence.
