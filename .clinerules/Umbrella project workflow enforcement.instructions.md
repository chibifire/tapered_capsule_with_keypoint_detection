---
applyTo: "**"
textId: "INST-043"
---

# Umbrella project workflow enforcement

When working with Elixir umbrella projects, all Mix commands must be executed from the umbrella root directory. Individual app compilation breaks the coordinated dependency management system.

## The principle

Umbrella projects coordinate dependencies, build paths, and compilation order across multiple applications. Running Mix commands from individual app directories bypasses this coordination and creates dependency conflicts.

## FORBIDDEN patterns

**NEVER do these operations:**

```bash
# BAD: Going into individual apps for Mix commands
cd apps/aria_engine_core && mix compile
cd apps/aria_timeline && mix test
cd apps/any_app && mix deps.get
```

**Why this breaks things:**

- Creates conflicting lock files
- Bypasses umbrella dependency coordination
- Causes environment specification conflicts
- Breaks shared build path management
- Results in "dependency overriding" errors

## REQUIRED patterns

**ALWAYS work from umbrella root:**

```bash
# GOOD: All operations from umbrella root
mix compile                           # Compiles all apps in dependency order
mix test                             # Runs all tests across all apps
mix test apps/aria_engine_core       # Tests specific app from root
mix deps.get                         # Manages dependencies for entire umbrella
mix deps.clean --all                 # Cleans all dependencies
```

## Specific workflows

**Compilation:**

```bash
# From umbrella root only
mix compile
mix compile --force
MIX_ENV=test mix compile
```

**Testing:**

```bash
# From umbrella root only
mix test                             # All apps
mix test apps/aria_engine_core       # Specific app
mix test apps/aria_engine_core/test/specific_test.exs  # Specific test
```

**Dependency management:**

```bash
# From umbrella root only
mix deps.get
mix deps.update package_name
mix deps.clean --all
```

**Development workflow:**

```bash
# From umbrella root only
mix format
mix credo
mix dialyzer
```

## Individual app operations

**When you need to work with specific apps:**

```bash
# CORRECT: Specify app from umbrella root
mix test apps/aria_engine_core
mix compile apps/aria_timeline
mix format apps/aria_state

# WRONG: Never cd into apps
cd apps/aria_engine_core  # FORBIDDEN for Mix commands
```

## Dependency conflict resolution

**When dependency conflicts occur:**

1. **Stay at umbrella root** - never cd into apps
2. **Clean everything:** `mix deps.clean --all`
3. **Regenerate dependencies:** `mix deps.get`
4. **Test compilation:** `mix compile`

**Fix mix.exs files from umbrella root:**

- Edit `apps/app_name/mix.exs` files directly
- Ensure consistent dependency specifications
- Remove conflicting environment specifications
- Use simple `in_umbrella: true` declarations

## Benefits of umbrella workflow

- **Coordinated dependencies:** All apps use consistent versions
- **Proper build order:** Dependencies compile before dependents
- **Shared configuration:** Consistent settings across all apps
- **Unified testing:** Run tests across entire system
- **Clean development:** No conflicting build artifacts

## Emergency recovery

**If umbrella gets broken by individual app compilation:**

1. **Return to umbrella root:** `cd /path/to/umbrella/root`
2. **Clean everything:** `mix clean && mix deps.clean --all`
3. **Remove broken artifacts:** `rm -rf _build deps`
4. **Regenerate:** `mix deps.get && mix compile`

## Enforcement

This rule is **mandatory** - any Mix command execution from individual app directories is prohibited. Always verify you're in the umbrella root before running Mix commands.

**Check your location:**

```bash
pwd  # Should show umbrella root, not apps/app_name
ls   # Should show apps/ directory and root mix.exs
```

This workflow ensures the umbrella project maintains its coordinated dependency management and prevents the "dependency overriding" errors that break compilation.
