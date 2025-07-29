---
applyTo: "**"
textId: "INST-037"
---

## Manual file cleanup assistance

### The Problem

During automated file modifications, extraneous content such as `final_file_content` blocks or other tool-related output might occasionally be accidentally inserted into source code or configuration files. This can lead to syntax errors, compilation failures, or other unexpected behavior.

### When to Assist

Your manual assistance is required when the model explicitly requests it to remove such accidentally inserted content.

### How to Assist

When requested, please follow these steps carefully:

1. **Locate the Specified File**: Open the file path provided by the model.
2. **Identify the Problematic Block**: Look for the `final_file_content` block. This block typically starts with `<final_file_content path="[file_path]">` and ends with `</final_file_content>`, often followed by `<environment_details>` and `</environment_details>`. The content within these tags is what needs to be removed.
3. **Manually Remove the Entire Block**: Delete all lines associated with the identified block, including the opening and closing XML tags (`<final_file_content>`, `</final_file_content>`, `<environment_details>`, `</environment_details>`) and any content between them.
4. **Save the File**: Ensure the file is saved after removing the content.
5. **Confirm to the Model**: Inform the model that the cleanup is complete.
