---
applyTo: "**"
textId: "INST-032"
---

## Phonetic Alphabet Options

When presenting options for a decision, always use the phonetic alphabet (Alpha, Bravo, Charlie, Delta, etc.) as identifiers for each option.

### Usage with `ask_followup_question`

Options should be provided as a JSON array of strings within the `options` parameter. The phonetic alphabet identifier should be included at the beginning of each option string.

Each option's description should be clear, concise, and provide sufficient detail for the user to make an informed decision. Avoid generic terms like "Confirm" or "Cancel" alone; instead, elaborate on what is being confirmed or cancelled.

* **Always include a "Commit" option:** For any decision point where changes have been made or are about to be made, include an option to `git commit` the changes. This option should be clearly labeled, for example: `"Echo: Commit current changes."`

Example:

```json
["Alpha: Proceed with adding temporary debugging statements.", "Bravo: Cancel the proposed code modification.", "Echo: Commit current changes."]
```

### Rationale

This ensures clear and consistent communication when presenting choices, making it easier for the user to select an option and understand the implications of their choice.
