---
applyTo: "**"
textId: "INST-040"
---

# Call Site → Leaf Node Testing Pattern

## The Principle

When modifying a schema or interface, trace changes from the call site down to all leaf node implementations, testing each affected component systematically.

## Implementation Approach

1. **Identify Call Sites**
   - Find all entry points that invoke the modified function/schema
   - Map the dependency chain from these call sites

2. **Trace to Leaf Nodes**
   - Follow execution paths to identify all leaf node functions
   - Leaf nodes are terminal implementation functions that directly handle the modified data structure

3. **Test-First Methodology**
   - Write tests for each leaf node before modifying implementation
   - Test both existing functionality and new requirements
   - Include edge cases specific to each leaf node's responsibilities

4. **Bottom-Up Fixing**
   - Fix leaf nodes first, verifying with tests
   - Work upward through the dependency chain
   - Ensure each layer correctly handles modified data from lower layers

5. **Integration Verification**
   - After fixing individual components, test the entire path
   - Verify data flows correctly from call site to leaf nodes and back

## Example for Open-Ended Intervals

1. **Schema Change**: Update `duration` to allow open-ended intervals
2. **Call Site**: `get_schedule_activities_definition`
3. **Leaf Nodes**:
   - `validate_duration/1` (validation logic)
   - `parse_datetime/2` (datetime parsing)
   - `convert_activities/1` (conversion to internal format)
4. **Test Cases**:
   - Only start time provided
   - Only end time provided
   - Both times provided
   - Invalid timezone formats
   - Edge cases for each leaf node

This pattern ensures comprehensive testing and implementation when modifying data structures that flow through multiple layers of your application.
