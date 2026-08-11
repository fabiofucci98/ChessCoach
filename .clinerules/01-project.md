# Cline Project Rules

## Editing
- Make the smallest possible change.
- Never rewrite an entire file for a small change.
- Prefer precise patches/edits.
- If an edit tool fails, do not repeatedly retry the same malformed operation.
- Inspect the relevant code before editing.
- Preserve unrelated code, formatting, imports, and behavior.
- After editing, inspect the changed section.

## Context Efficiency
- Search for relevant symbols before opening files.
- Read only the files/sections needed for the task.
- Do not scan the entire repository unnecessarily.
- Do not read generated/dependency directories.

## Scope
- Modify only files necessary for the requested task.
- Do not refactor unrelated code.
- Do not add dependencies unless necessary.
- Reuse existing utilities, patterns, and libraries.

## Verification
- Run the smallest relevant test/check after changes.
- Fix only failures related to the current task.
- Do not run expensive full builds/tests unless necessary.

## Safety
- Never delete or overwrite large amounts of code without justification.
- Never perform destructive database operations without confirmation.
- Never expose or modify secrets in `.env` files.

## Communication
- Keep responses concise.
- For simple tasks, implement directly.
- For large/ambiguous tasks, inspect first and explain the plan before making major changes.