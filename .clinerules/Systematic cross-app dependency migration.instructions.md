---
applyTo: "apps/**"
textId: "INST-042"
---

# Systematic cross-app dependency migration

When migrating cross-app dependencies in umbrella projects, use a systematic group-based approach that addresses all violations comprehensively rather than fixing apps individually. This ensures complete architectural compliance and prevents missed violations.

## The principle

Cross-app dependency violations must be addressed systematically across the entire codebase as coordinated groups, not as isolated per-app fixes. Individual app fixes miss the interconnected nature of dependency violations and can leave architectural inconsistencies.

## Mandatory tooling requirements

**REQUIRED: Use `ast_migrate` for all Elixir code analysis and transformation**

All cross-app dependency migration work MUST use the `ast_migrate` app for systematic AST-based analysis and transformation. This ensures accurate, comprehensive detection and safe code modifications.

**PROHIBITED approaches:**

- **CLI inspection tools:** `grep`, `find`, `awk`, `sed`, or any text-based pattern matching
- **Regex-based analysis:** Regular expressions for code pattern detection
- **Manual repetitive inspection:** Ad-hoc file-by-file examination
- **Text-based search and replace:** Any non-AST-aware code modification

## Systematic detection methodology

**Phase 1: Comprehensive violation mapping using `ast_migrate`**

1. **Audit entire codebase:** Use `ast_migrate` to identify all cross-app dependency patterns
2. **Categorize by violation type:** Group violations by the type of architectural boundary crossed
3. **Map dependency chains:** Identify which apps depend on which internal modules
4. **Quantify scope:** Count violations per category to understand migration scope

**Essential violation categories:**

- **Legacy namespace violations:** `AriaEngine.*` patterns that should use proper app APIs
- **Internal module imports:** Direct imports of `App.Internal.Module` across app boundaries
- **State/domain violations:** Direct usage of internal state/domain modules
- **Timeline violations:** Internal timeline module usage instead of external APIs

## Group-based fixing approach

**Fix by violation type, not by app:**

1. **Type A violations:** All `AriaEngine.Timeline.*` → `AriaTimeline` API calls
2. **Type B violations:** All `AriaEngineCore.*` direct usage → `AriaEngineCore` API calls  
3. **Type C violations:** All `AriaTimeline.TimelineCore.*` → `AriaTimeline` API calls
4. **Type D violations:** All remaining internal module imports across apps

**Dependency-order implementation:**

- **Infrastructure apps first:** Core dependencies (aria_core, aria_state, aria_serial)
- **Foundation apps second:** Timeline and storage layers
- **Planning apps third:** Hybrid planner and engine core
- **Application layer last:** UI and integration apps

## Implementation strategy

**For each violation type:**

1. **Search and catalog:** Find all instances of the violation pattern
2. **Identify missing APIs:** Determine what external API functions are needed
3. **Implement missing APIs:** Add required functions to external modules
4. **Apply fixes systematically:** Update all violations of this type across all apps
5. **Validate immediately:** Compile and test after each violation type is fixed

**Required `ast_migrate` analysis patterns:**

Use `ast_migrate` to systematically detect violation patterns through AST analysis:

```elixir
# Use ast_migrate for comprehensive violation detection
# - Legacy namespace violations (AriaEngine.*, AriaCore.*)
# - Internal module imports across app boundaries
# - Direct internal usage patterns
# - Cross-app dependency chains

# ast_migrate provides accurate AST-based detection that cannot miss
# violations due to text formatting, comments, or complex expressions
```

## External API completeness verification

**Before fixing violations:**

1. **Audit external APIs:** Ensure all needed functions exist in `lib/app_name.ex` files
2. **Identify gaps:** Find functions that violations need but APIs don't provide
3. **Implement missing functions:** Add required delegation functions to external APIs
4. **Document API coverage:** Ensure external APIs provide complete functionality

**API implementation pattern:**

```elixir
# In lib/app_name.ex
def needed_function(args) do
  AppName.Internal.Module.needed_function(args)
end
```

## Validation requirements

**After each violation type fix:**

1. **Compilation verification:** All apps must compile without errors
2. **Test execution:** Run test suites to verify functionality preservation
3. **Cross-app integration:** Verify that app interactions still work correctly
4. **Performance validation:** Ensure no significant performance regressions

**Comprehensive final validation:**

- **No internal imports:** Search confirms no cross-app internal module usage
- **API completeness:** All needed functionality available through external APIs
- **Functional equivalence:** All features work the same as before migration
- **Clean architecture:** Clear boundaries between apps with proper encapsulation

## Benefits of systematic approach

- **Complete coverage:** No violations missed due to systematic detection
- **Architectural consistency:** All apps follow the same external API patterns
- **Maintainable codebase:** Clear boundaries prevent future violations
- **Coordinated migration:** Dependencies fixed in proper order
- **Verifiable compliance:** Systematic validation ensures complete migration

## What to avoid

- **Per-app fixing:** Addressing violations one app at a time misses interconnections
- **Partial migration:** Leaving some violation types unfixed creates inconsistent architecture
- **Missing API functions:** Fixing violations without ensuring external APIs are complete
- **Inadequate validation:** Not verifying that all functionality is preserved

## Prohibited approaches and rationale

**NEVER use these error-prone methods:**

- **CLI text tools (grep, find, sed, awk):** Miss violations due to formatting variations, comments, and complex expressions
- **Regex pattern matching:** Cannot understand Elixir syntax context and produces false positives/negatives
- **Manual inspection:** Inconsistent, time-consuming, and prone to human error
- **Ad-hoc search and replace:** Breaks code by not understanding AST structure and dependencies

**Why `ast_migrate` is mandatory:**

- **AST-aware analysis:** Understands Elixir code structure, not just text patterns
- **Comprehensive detection:** Cannot miss violations due to formatting or syntax variations
- **Safe transformations:** Preserves code semantics while making systematic changes
- **Systematic approach:** Ensures consistent application across entire codebase
- **Validation integration:** Provides compilation and test verification of changes

## Implementation tracking

**Document progress systematically:**

```markdown
## Cross-App Dependency Migration Progress

### Violation Type A: AriaEngine.Timeline.* → AriaTimeline
- **Total violations:** 45 found
- **Apps affected:** aria_timeline, aria_hybrid_planner, aria_engine_core
- **Status:** ✅ Complete - All violations fixed and tested

### Violation Type B: AriaEngineCore.* → AriaEngineCore API
- **Total violations:** 78 found  
- **Apps affected:** aria_hybrid_planner, aria_town, aria_membrane_pipeline
- **Status:** 🔄 In Progress - 45/78 violations fixed

### External API Gaps Identified:
- ✅ AriaTimeline.create_interval - Added
- 🔄 AriaEngineCore.execute_action - In progress
- ⏳ AriaEngineCore.set_fact - Pending
```

## Success criteria

**Migration complete when:**

- **Zero cross-app internal imports:** No `alias App.Internal.Module` patterns across apps
- **Complete external APIs:** All needed functionality available through `lib/app_name.ex` files
- **Full compilation:** All apps compile without warnings or errors
- **Functional preservation:** All tests pass and features work as before
- **Clean architecture:** Apps communicate only through external APIs

This systematic approach ensures umbrella projects achieve true architectural encapsulation with maintainable, well-bounded app interfaces.
