# Capsule Sizing Guide

This guide provides recommendations for the number of capsules to use when generating tapered capsules for different types of avatars.

## Recommended Capsule Counts

### Humanoid Avatars

| Avatar Type | Recommended Capsules | Notes |
|-------------|---------------------|-------|
| Feminine Avatar | 8-12 | Good balance between accuracy and performance |
| Male Avatar | 8-12 | Similar to feminine avatars |
| Child Avatar | 6-10 | Fewer capsules needed for smaller frame |
| Detailed Avatar | 12-20 | More capsules for complex clothing/accessories |

### Non-Humanoid Avatars

| Avatar Type | Recommended Capsules | Notes |
|-------------|---------------------|-------|
| Animal (Pet) | 4-8 | Simple body structure |
| Animal (Complex) | 8-15 | Detailed anatomy |
| Fantasy Creature | 10-25 | Varies greatly with design |
| Robot/Mech | 6-15 | Depends on joint complexity |

## Factors Affecting Capsule Count

### Anatomy Complexity
- **Simple**: Basic humanoid structure (8-10 capsules)
- **Moderate**: Additional limbs or features (10-15 capsules)
- **Complex**: Multiple appendages, tail, wings (15-25 capsules)

### Performance Considerations
- **Real-time applications**: Fewer capsules (6-12)
- **Offline rendering**: More capsules acceptable (12-25)
- **Mobile platforms**: Optimize for lower counts (4-10)

### Quality Requirements
- **Low fidelity**: Minimal capsules for basic collision (4-8)
- **Medium fidelity**: Balanced representation (8-15)
- **High fidelity**: Detailed coverage (15-30+)

## Testing Recommendations

### Starting Point
For a representative feminine avatar, start with **10 capsules** as a baseline.

### Iterative Approach
1. Start with a lower count (6-8)
2. Gradually increase until visual quality is acceptable
3. Monitor performance impact
4. Adjust based on specific avatar features

### Validation
- Check coverage of major body parts
- Verify joint areas are properly represented
- Test animation compatibility
- Validate collision detection accuracy

## Example: Feminine VRM Avatar
For the `fem_vroid.vrm` test avatar:
- **Minimum viable**: 6 capsules
- **Recommended**: 10 capsules
- **High detail**: 15 capsules

This provides a good balance between:
- Accurate body representation
- Reasonable computational cost
- Smooth animation performance
