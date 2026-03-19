# Test Cases: Create New Scheduler Page

**Design Reference:** [Figma – EkoAI Console 2026](https://www.figma.com/design/scJyrNxS1YKjrWvj6E4ZUj/EkoAI-Console-2026?node-id=325-8465&m=dev)
**Page Description:** A form to set up a new automated task scheduler, consisting of three sections: Create New, AI Agentic Process, and Set Action.

---

## 1. Page Layout & Header

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-001 | Page title displays correctly | Navigate to the Create New Scheduler page | Title "Create New Scheduler" is displayed in bold (24px, #212121) |
| TC-002 | Page subtitle displays correctly | Navigate to the Create New Scheduler page | Subtitle "Set up a new automated task scheduler" is displayed below the title (12px, #9E9E9E) |
| TC-003 | Cancel button is visible | Navigate to the Create New Scheduler page | "Cancel" text button is displayed in the top-right area (#616161) |
| TC-004 | Create button is visible | Navigate to the Create New Scheduler page | "Create" primary button is displayed with green background (#04BE8C) and white text |
| TC-005 | Navbar is visible on the left | Navigate to the Create New Scheduler page | Dark sidebar (#212121) with navigation icons is displayed on the left side (72px wide) |

---

## 2. Section: Create New (💼)

### 2.1 Scheduler Name (Required)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-010 | Scheduler Name label with asterisk | View the form | Label "Scheduler Name" is displayed with a red asterisk (*) indicating required field |
| TC-011 | Scheduler Name placeholder | View the Scheduler Name input | Placeholder text "Enter scheduler name" is displayed (#9E9E9E) |
| TC-012 | Enter valid scheduler name | Type a valid name (e.g., "Daily Report") into the field | The input accepts and displays the entered text |
| TC-013 | Leave Scheduler Name empty and submit | Leave the field empty and click "Create" | Validation error is shown; form is not submitted |
| TC-014 | Enter scheduler name with max length | Type a very long name (e.g., 256+ characters) | The system either truncates or shows a max-length validation error |
| TC-015 | Enter scheduler name with special characters | Type special characters (e.g., `<script>alert('x')</script>`) | Input is sanitized; no XSS is executed |
| TC-016 | Enter scheduler name with only spaces | Type only spaces and click "Create" | Validation error is shown; whitespace-only names are not accepted |

### 2.2 Description (Optional)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-020 | Description label without asterisk | View the form | Label "Description" is displayed without a red asterisk (optional field) |
| TC-021 | Description placeholder | View the Description textarea | Placeholder text "Enter description" is displayed (#9E9E9E) |
| TC-022 | Enter description text | Type a description into the textarea | The textarea accepts and displays multi-line text |
| TC-023 | Leave Description empty and submit | Fill all required fields, leave Description empty, click "Create" | Form submits successfully without description |
| TC-024 | Description textarea height | View the Description field | Textarea has an appropriate height (~104px) for multi-line input |

### 2.3 Repeat (Dropdown)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-030 | Repeat label is displayed | View the form | Label "Repeat" is displayed (16px, semibold, #212121) |
| TC-031 | Repeat default value | View the Repeat dropdown | Default value "Does not repeat" is displayed |
| TC-032 | Open Repeat dropdown | Click on the Repeat dropdown | Dropdown menu opens showing available repeat options |
| TC-033 | Select a repeat option | Open dropdown and select an option (e.g., "Daily", "Weekly") | Selected option is displayed in the dropdown field |
| TC-034 | Dropdown chevron icon | View the Repeat dropdown | A down-arrow (angle-down) icon is displayed on the right side (#BDBDBD) |

---

## 3. Section: AI Agentic Process (⏰)

### 3.1 Schedule Time

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-040 | Schedule Time label is displayed | View the AI Agentic Process section | Label "Schedule Time" is displayed (16px, semibold, #212121) |
| TC-041 | Schedule Time placeholder with icon | View the Schedule Time field | Placeholder "Select start time" is displayed with a clock/time icon on the left |
| TC-042 | Select a start time | Click the Schedule Time field and select a time | The selected time is displayed in the field |
| TC-043 | Schedule Time field has proper border | View the Schedule Time field | Field has a border (#E5E5E5), rounded corners (8px), and white background |

### 3.2 Custom Webhook URL (Required)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-050 | Custom webhook URL label with asterisk | View the form | Label "Custom webhook URL" is displayed with a red asterisk (*) indicating required field |
| TC-051 | Webhook URL placeholder | View the Custom webhook URL input | Placeholder text "Enter webhook URL" is displayed (#9E9E9E) |
| TC-052 | Enter valid webhook URL | Type a valid URL (e.g., `https://example.com/webhook`) | The input accepts and displays the entered URL |
| TC-053 | Leave webhook URL empty and submit | Fill other required fields but leave webhook URL empty, click "Create" | Validation error is shown; form is not submitted |
| TC-054 | Enter invalid URL format | Type an invalid URL (e.g., "not-a-url") | Validation error is shown indicating invalid URL format |
| TC-055 | Enter webhook URL with special characters | Type a URL with script injection (e.g., `javascript:alert(1)`) | Input is sanitized; dangerous protocols are rejected |

---

## 4. Section: Set Action (⭐️)

### 4.1 Action (Dropdown)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-060 | Action label is displayed | View the Set Action section | Label "Action" is displayed (16px, semibold, #212121) |
| TC-061 | Action dropdown default value | View the Action dropdown | Default value "Morning Brief Widget" is displayed |
| TC-062 | Action dropdown has gray background | View the Action dropdown | Dropdown has a gray background (#F5F5F5) with border (#E5E5E5) |
| TC-063 | Open Action dropdown | Click on the Action dropdown | Dropdown menu opens showing available actions |
| TC-064 | Select a different action | Open dropdown and select a different action | Selected action is displayed; related fields may update accordingly |
| TC-065 | Action dropdown chevron icon | View the Action dropdown | A down-arrow (angle-down) icon is displayed on the right side (#BDBDBD) |

### 4.2 Schedule Time (Radio Buttons)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-070 | Schedule Time label in Set Action section | View the Set Action section | A second "Schedule Time" label is displayed under the Action field |
| TC-071 | "As soon as the response is ready" default selected | View the radio buttons | "As soon as the response is ready" radio button is selected by default (green dot) |
| TC-072 | "Set time" radio button is unselected | View the radio buttons | "Set time" radio button is unselected by default |
| TC-073 | Select "Set time" option | Click on the "Set time" radio button | "Set time" is selected; "As soon as the response is ready" is deselected |
| TC-074 | Select "As soon as the response is ready" | After selecting "Set time", click on "As soon as the response is ready" | "As soon as the response is ready" is selected; "Set time" is deselected |
| TC-075 | Only one radio option selected at a time | Click between the two radio options | Only one radio button can be selected at any time (mutual exclusivity) |
| TC-076 | "Set time" reveals time picker | Select the "Set time" radio button | A time picker or time input field appears below the radio button |

---

## 5. Form Submission

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-080 | Submit with all required fields filled | Fill "Scheduler Name", "Custom webhook URL", and all other fields; click "Create" | Scheduler is created successfully; user is redirected or sees a success message |
| TC-081 | Submit with only required fields | Fill only "Scheduler Name" and "Custom webhook URL"; click "Create" | Scheduler is created with default values for optional fields |
| TC-082 | Submit with empty required fields | Leave all fields empty and click "Create" | Validation errors are shown for "Scheduler Name" and "Custom webhook URL" |
| TC-083 | Cancel button navigates back | Click "Cancel" | User is navigated back to the previous page without saving any data |
| TC-084 | Cancel with unsaved changes | Fill some fields and click "Cancel" | A confirmation dialog appears asking if the user wants to discard changes |
| TC-085 | Double-click Create button | Fill all required fields and double-click "Create" quickly | Only one scheduler is created (duplicate submission prevention) |

---

## 6. Section Dividers & Visual Design

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-090 | Section divider between "Create new" and "AI Agentic Process" | View the form | A horizontal divider line (#E5E5E5) separates the two sections |
| TC-091 | Section divider between "AI Agentic Process" and "Set Action" | View the form | A horizontal divider line (#E5E5E5) separates the two sections |
| TC-092 | Section headers with emoji icons | View all section headers | "💼 Create new", "⏰ AI Agentic Process", and "⭐️ Set Action" are displayed with correct emojis (14px, semibold, #616161) |
| TC-093 | Input field styling consistency | View all text input fields | All inputs have consistent styling: white bg, #E5E5E5 border, 8px border-radius, 12px padding |
| TC-094 | Required field indicators | View all form labels | Only "Scheduler Name" and "Custom webhook URL" show red asterisks (*) |

---

## 7. Responsive & Accessibility

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-100 | Keyboard navigation | Use Tab key to navigate through all form fields | Focus moves in logical order: Scheduler Name → Description → Repeat → Schedule Time → Webhook URL → Action → Schedule Time radios → Cancel → Create |
| TC-101 | Screen reader labels | Use a screen reader on the form | All form fields have appropriate accessible labels; required fields are announced as required |
| TC-102 | Form field focus states | Click/tab into each input field | Focused fields show a visible focus indicator (e.g., border color change) |
| TC-103 | Error messages are accessible | Submit form with empty required fields | Error messages are associated with their respective fields and announced by screen readers |
| TC-104 | Color contrast compliance | Inspect text and background colors | All text meets WCAG 2.1 AA contrast requirements (e.g., #212121 on white, #9E9E9E placeholder text) |
