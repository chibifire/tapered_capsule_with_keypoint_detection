---
applyTo: "**"
textId: "INST-030"
---

## Commit timing flexibility

When working on complex technical implementations, prioritize finding meaningful commit points over adhering to strict timing constraints. Quality and logical grouping of changes take precedence over immediate commits.

### The principle

While frequent commits are generally good practice, complex technical work often requires extended development sessions to reach a stable, logical commit point. It's better to delay committing until the code reaches a coherent state than to commit broken or incomplete implementations.

### When to delay commits

**Acceptable delay scenarios:**

- **Complex algorithm implementation:** When working on intricate algorithms like PC-2, Floyd-Warshall, or other mathematical implementations that require multiple interdependent changes
- **API refactoring:** When restructuring interfaces that affect multiple modules and require coordinated changes
- **Test suite alignment:** When fixing compilation errors across multiple test files that share common dependencies
- **Documentation recovery:** When reconstructing lost documentation or comments that provide essential context
- **Architecture cleanup:** When removing technical debt that spans multiple files and functions

### Finding good commit points

**Look for these natural boundaries:**

- **Compilation success:** All files compile without errors or warnings
- **Test stability:** Even if some tests fail, they fail for logical reasons rather than compilation issues
- **Functional completeness:** A specific feature or algorithm is implemented end-to-end
- **API consistency:** All related functions have matching signatures and documentation
- **Documentation alignment:** Code changes are accompanied by updated or recovered documentation

### Risk of topic switching

**⚠️  CRITICAL WARNING - TOTAL LOSS RISK ⚠️**

If the development focus starts switching between different topics or areas of the codebase, it becomes very easy to get lost fast and leave the code in an uncommittable state.

**UNCOMMITTABLE CODE = TOTAL LOSS OF ALL WORK**

If you cannot reach a stable commit point, all progress will be permanently lost. This is not theoretical - it is the primary risk when working across multiple complex modules simultaneously.

When you notice topic drift occurring:

1. **STOP IMMEDIATELY** - Do not continue working on the new topic
2. **Assess current state** - Can any subset of current changes be committed?
3. **Force a commit point** - Even if imperfect, commit what compiles rather than risk total loss
4. **Use git stash strategically** - Isolate unrelated changes if necessary
5. **Accept imperfection** - A working-but-incomplete commit is infinitely better than total loss

**Dangerous topic switching examples:**

- Working on PC-2 algorithm → switching to test organization → adding new features
- Debugging intervals → refactoring Allen relations → fixing documentation
- Any pattern where you touch 3+ different areas without committing intermediate progress

**If already in uncommittable state:**

- Identify minimal viable subset that compiles
- Commit partial work with clear "WIP:" prefix in commit message
- Document what remains incomplete in commit message
- Never attempt to "fix just one more thing" without committing first
- **Commit current progress:** Even if imperfect, get the current work committed
- **Create a new branch:** Start fresh for the new topic area
- **Document the switch:** Note why you're changing focus and what remains to complete

### Consequences of uncommittable states

**What leads to total loss:**

- **Multiple broken compilation units:** Changes spread across too many files to fix systematically
- **Circular dependencies:** Modifications that create unsolvable dependency loops
- **API mismatches:** Function signature changes that break too many call sites simultaneously
- **Test framework conflicts:** Changes that break the testing infrastructure itself
- **Mixed incomplete features:** Multiple half-implemented features that cannot be separated

**Recovery strategies:**

- **Frequent intermediate commits:** Even with compilation warnings, commit logical progress points
- **Branch early and often:** Separate experimental work from stable progress
- **Document decision points:** Record why changes were made to aid in untangling complex states
- **Maintain one working state:** Always have at least one recent commit that represents functional code

- **Immediately assess commit readiness:** Check if current changes can be committed as-is
- **Commit partial progress:** Even incomplete work is better than mixed-topic confusion
- **Document switching points:** Note where you stopped one topic to begin another
- **Resist scope creep:** Stay focused on the current implementation rather than jumping to related problems

Topic switching is one of the fastest ways to create uncommittable code states that require significant untangling effort.

### What constitutes a meaningful commit

**Quality indicators:**

- **Coherent scope:** All changes serve a single, well-defined purpose
- **Functional integrity:** The codebase is in a better state than before the changes
- **Clear narrative:** The commit message can accurately describe what was accomplished
- **Reduced complexity:** Technical debt has been addressed rather than added
- **Preserved knowledge:** Important implementation details and reasoning are documented

### Communication during extended sessions

**Keep stakeholders informed:**

- **Document progress:** Update relevant ADRs or comments about current work
- **Explain delays:** Communicate why finding a good commit point is taking longer
- **Share discoveries:** Note important findings or architectural insights gained during the work
- **Outline remaining work:** Clarify what needs to be completed to reach the commit point

### Benefits

- **Higher quality commits:** Each commit represents meaningful, stable progress
- **Better debugging:** Future developers can understand what each commit accomplished
- **Cleaner history:** Logical grouping of changes makes the project history more useful
- **Reduced rework:** Taking time to get things right reduces the need for immediate follow-up fixes
- **Preserved context:** Complex implementations retain their essential documentation and reasoning

### Balance with project needs

**Consider these factors:**

- **Blocking dependencies:** Whether other work is waiting on these changes
- **Risk management:** How long the current branch has diverged from main
- **Backup strategy:** Whether work is safely preserved in case of interruption
- **Team coordination:** Whether extended delays affect other team members

This approach recognizes that thoughtful, well-structured commits are more valuable than rushed commits that create technical debt or confusion.
