---
applyTo: "apps/**"
textId: "INST-045"
---

# Cross-app architectural boundary correction

When umbrella app architecture violations are discovered, systematically evaluate whether the solution requires app boundary restructuring rather than simple module flattening or delegation fixes.

## The principle

Architectural violations in umbrella projects often indicate incorrect app boundaries rather than just module nesting issues. The solution may require extracting functionality to new apps or migrating functions to more appropriate existing apps, achieving proper separation of concerns.

## Investigation methodology

**Phase 1: Identify violation type**

1. **Module depth violations:** 3+ level nesting (e.g., `App.Domain.SubModule`)
2. **Mixed concerns within apps:** Domain + math + execution logic in single app
3. **Cross-cutting functionality:** Shared logic that belongs in dedicated app
4. **Logical boundary misalignment:** Functions in apps that don't match their core responsibility

**Phase 2: Determine correction approach**

**Extract to new app when:**

- **Distinct domain:** Functionality represents a separate logical domain (math, auth, storage)
- **Cross-app reuse:** Multiple apps need the same functionality
- **Specialized expertise:** Functionality requires domain-specific knowledge
- **Independent evolution:** Logic changes independently from current app

**Migrate to existing app when:**

- **Natural fit:** Functionality logically belongs in existing app's domain
- **Single consumer:** Only one app currently uses the functionality
- **Tightly coupled:** Functionality is closely related to existing app's core purpose

**Flatten within app when:**

- **Simple nesting issue:** Only module depth violation, proper app boundary
- **App-specific logic:** Functionality is unique to current app's domain
- **No separation benefit:** Extraction would not improve architecture

## Separation of concerns patterns

**Standard app responsibility patterns:**

- **Core apps** (`aria_core`, `aria_state`): Domain management, fundamental data structures
- **Math apps** (`aria_math`): Mathematical operations, algorithms, data transformations
- **Execution apps** (`aria_engine_core`, `aria_hybrid_planner`): Workflow coordination, execution logic
- **Storage apps** (`aria_storage`, `aria_timeline`): Data persistence, retrieval, timeline management
- **Interface apps** (`aria_town`, `aria_membrane_pipeline`): External integrations, API boundaries
- **Utility apps** (`aria_serial`, `aria_auth`): Cross-cutting concerns, shared utilities

## Implementation strategy

**For new app extraction:**

1. **Create umbrella app:** Use `mix new app_name --sup` in apps directory
2. **Design external API:** Create clean, focused external module (`lib/app_name.ex`)
3. **Move implementation files:** Transfer modules to new app with proper naming
4. **Update module definitions:** Change module names to match new app namespace
5. **Add dependency declarations:** Update `mix.exs` files for inter-app dependencies
6. **Update cross-app references:** Change all external calls to use new app's external API
7. **Remove empty directories:** Clean up original app structure

**For existing app migration:**

1. **Identify target app:** Determine which existing app should own the functionality
2. **Enhance target external API:** Add required delegation functions to target app
3. **Move implementation files:** Transfer modules to target app with namespace updates
4. **Update source app:** Change delegations to point to target app's external API
5. **Verify cross-app calls:** Ensure all external references use proper APIs

## External API design patterns

**For newly extracted apps:**

```elixir
# Clean, focused external API
defmodule AppName do
  # Group related functionality logically
  
  # Primary operations
  defdelegate core_operation(args), to: AppName.Core
  defdelegate primary_function(args), to: AppName.Primary
  
  # Secondary operations
  defdelegate utility_function(args), to: AppName.Utilities
  defdelegate helper_operation(args), to: AppName.Helpers
  
  # Maintain 2-level depth maximum for internal modules
end
```

**Integration with existing external APIs:**

```elixir
# Source app delegates to target app
defmodule SourceApp do
  # Remove internal implementations, delegate to appropriate apps
  defdelegate domain_operation(args), to: AriaCore
  defdelegate math_operation(args), to: AriaMath
  defdelegate execution_operation(args), to: ExecutionApp
end
```

## Validation requirements

**Architectural compliance verification:**

1. **No 3+ level nesting:** All module paths follow `App.Module` or `App.Internal.Module` pattern
2. **Clear separation of concerns:** Each app has focused, well-defined responsibility
3. **External API completeness:** All cross-app communication uses external APIs
4. **Proper dependency management:** Umbrella dependencies correctly declared
5. **Compilation success:** All apps compile without errors after restructuring

**Testing verification:**

- **Functional preservation:** All existing functionality continues to work
- **API boundary respect:** No cross-app internal module imports
- **Performance maintenance:** No significant performance regressions
- **Documentation accuracy:** External APIs properly documented

## Common patterns and examples

**Math functionality extraction:**

```elixir
# BEFORE: AriaEngineCore.Math.Quaternion (3 levels - VIOLATION)
# AFTER: AriaMath.Quaternion (new app extraction)

# Move files:
apps/aria_engine_core/lib/aria_engine_core/math/ → apps/aria_math/lib/aria_math/

# Update references:
AriaEngineCore.Math.Quaternion → AriaMath.Quaternion
```

**Domain functionality migration:**

```elixir
# BEFORE: AriaEngineCore.Domain.Methods (3 levels - VIOLATION)  
# AFTER: AriaCore.Methods (migrate to existing app)

# Move files:
apps/aria_engine_core/lib/aria_engine_core/domain/ → apps/aria_core/lib/aria_core/

# Update references:
AriaEngineCore.Domain.Methods → AriaCore.Methods
```

## Integration with existing instructions

**Builds on:**

- **INST-041:** Apps todo file management - provides umbrella app structure requirements
- **INST-042:** Systematic cross-app dependency migration - handles dependency fixing
- **INST-044:** Investigate before implementing tombstone pattern - provides investigation methodology

**Complements:**

- **INST-017:** Targeted solutions over generalized systems - each app serves focused purpose
- **INST-019:** Local solutions over core modifications - keeps functionality in appropriate apps

## Benefits

- **Proper separation of concerns:** Each app has clear, focused responsibility
- **Maintainable architecture:** Changes isolated to appropriate app boundaries
- **Reusable functionality:** Extracted apps can serve multiple consumers
- **Compliance with standards:** Meets umbrella app architectural requirements
- **Scalable structure:** Architecture supports future growth and modification

## What to avoid

- **Over-extraction:** Creating apps for functionality that belongs in existing apps
- **Under-extraction:** Leaving mixed concerns within single apps
- **Incomplete migration:** Partial moves that leave architecture in inconsistent state
- **API pollution:** Adding functions to external APIs that don't belong to app's domain
- **Dependency violations:** Cross-app internal module imports after restructuring

This approach ensures umbrella projects maintain clean architectural boundaries that support long-term maintainability and proper separation of concerns.
