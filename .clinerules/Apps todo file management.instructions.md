---
applyTo: "apps/**"
textId: "INST-041"
---

# Apps todo file management

The `apps/todo.md` file serves as the central tracking document for umbrella app architectural restructuring. All apps must follow the standard Elixir pattern of only one external module with nested internal modules, and cross-app communication must use external module APIs exclusively.

## The principle

Each Elixir app in the umbrella project must have a clear public API boundary through a main external module file, with all internal implementation details properly encapsulated. The `apps/todo.md` file tracks progress on this architectural migration.

Prioritize the external elixir APIs first.

## Standard Elixir app pattern requirements

**Mandatory app structure:**

```
apps/app_name/
├── lib/
│   ├── app_name.ex          # External API module (REQUIRED)
│   └── app_name/            # Internal modules directory
│       ├── module_a.ex      # Internal implementation
│       ├── module_b.ex      # Internal implementation
│       └── subdirectory/    # Nested internal modules
├── test/
└── mix.exs
```

**External module responsibilities:**

- **Public API definition:** All functions that other apps need to call
- **Documentation:** Clear module documentation with examples
- **Delegation:** Delegate to internal modules for implementation
- **Abstraction:** Hide implementation details from external consumers

**Internal module responsibilities:**

- **Implementation details:** Core functionality and business logic
- **Private APIs:** Functions only used within the same app

## Cross-app communication rules

**FORBIDDEN patterns:**

```elixir
# BAD: Direct import of internal modules from other apps
alias AriaCore.Domain.SomeInternalModule
alias AriaEngine.Planner.InternalStrategy

# BAD: Calling internal functions directly
AriaCore.Domain.SomeInternalModule.private_function()
```

**REQUIRED patterns:**

```elixir
# GOOD: Only use external module APIs
alias AriaCore
alias AriaEngine

# GOOD: Call through public API
AriaCore.process_domain_data(data)
AriaEngine.execute_plan(plan)
```

## Module Size Guidelines

**Tiered line limits for maintainability:**

- **200-300 lines**: Review and consider splitting (soft threshold)
- **400-500 lines**: Strong recommendation to split (firm threshold)  
- **500+ lines**: Mandatory splitting (hard limit)

## Check using CLI tooling

- `wc`
- `mix format --check-formatted`
- `mix xref unavailable --include-siblings`
- `mix xref deprecated --include-siblings`

**Context-sensitive considerations:**

- **External API modules** (`lib/app_name.ex`): May exceed soft threshold since they primarily delegate to internal modules
- **Internal implementation modules**: Should stay closer to 200-300 lines for focused responsibility
- **Complex algorithms**: May warrant slightly higher limits if splitting would harm algorithmic coherence
- **Generated or templated code**: Different rules may apply based on generation patterns

**Integration with restructuring process:**

- **During API creation**: Split oversized internal modules before creating external API
- **Priority order**: Address module size issues in leaf apps first, following dependency chain
- **Documentation requirement**: Document splitting rationale in external API module comments

## Apps todo file management

**Track restructuring progress:**

- **Leaf apps first:** Start with apps that have no dependencies on other internal apps
- **Dependency order:** Work upward through the dependency chain
- **API creation:** Document when external APIs are established
- **Migration status:** Track which apps are compliant vs need restructuring

**Required todo file sections:**

```markdown
## Restructuring Progress

### Compliant Apps (✅)
- aria_serial - Has external API, proper structure
- aria_membrane_pipeline - Has external API, proper structure

### Needs External API (🔧)
- aria_core - Missing lib/aria_core.ex external module
- aria_auth - Missing lib/aria_auth.ex external module

### Cross-App Dependencies to Update (📋)
- Update AriaEngine calls to use AriaCore external API
- Migrate AriaHybridPlanner to use AriaTimeline external API
```

## Implementation process

**For each non-compliant app:**

1. **Create external module file:** Add `lib/app_name.ex` with public API
2. **Identify public functions:** Determine which functions other apps need
3. **Design clean API:** Create intuitive, well-documented public interface
4. **Delegate to internals:** Have external module delegate to existing internal modules
5. **Update cross-app calls:** Modify other apps to use new external API
6. **Remove internal imports:** Eliminate direct imports of internal modules
7. **Update todo file:** Mark app as compliant and document API availability

**Priority order:**

**For app restructuring (creating external APIs):**

- Apps with no dependencies on other internal modules (leaf apps first)
- Apps that are dependencies of other apps
- Core infrastructure apps (aria_core, aria_state)
- Higher-level apps that depend on multiple other apps

**For external API completion (after all apps have external API files):**

- Use AST migration tool to identify which external APIs have the most missing functions
- Complete APIs based on actual cross-app usage patterns (biggest gaps first)
- Prioritize by violation count rather than dependency hierarchy
- Complete each app's external API fully before moving to the next

## Enforcement rules

**Code review requirements:**

- **No internal module imports:** Cross-app imports must only use external modules
- **API completeness:** External modules must provide all needed functionality
- **Documentation quality:** External APIs must have clear documentation and examples
- **Backward compatibility:** API changes must not break existing consumers

**Testing requirements:**

- **External API tests:** Test all public functions in external modules
- **Integration tests:** Verify cross-app communication works through external APIs
- **Internal isolation:** Internal modules should not be directly tested by other apps

## Benefits

- **Clear boundaries:** Each app has a well-defined public interface
- **Maintainable code:** Changes to internal modules don't affect other apps
- **Better documentation:** External APIs force clear documentation of app capabilities
- **Easier refactoring:** Internal implementation can change without breaking other apps
- **Dependency management:** Clear understanding of what each app provides and consumes

## What to avoid

- **Bypassing external APIs:** Never import internal modules from other apps
- **Incomplete APIs:** External modules must provide all necessary functionality
- **Poor documentation:** External APIs without clear usage examples
- **Circular dependencies:** Apps depending on each other's internal modules

This restructuring ensures the umbrella project maintains clean architectural boundaries and supports long-term maintainability as the codebase grows.
