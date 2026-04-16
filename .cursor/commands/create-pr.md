# Create PR

Automates the creation of a GitHub Pull Request.

## Execution

1. Read the `.agents/skills/github-pr-creation/SKILL.md` skill and follow its workflow.
2. Apply the **Project-Specific Overrides** defined below, replacing the default behaviors in the skill.

## Project-Specific Overrides

When executing the PR creation, adhere to these project-specific requirements.

### Context & Hardcoded Values

- **Repository**: If the repository is not mentioned by the user, ask: _"Which repository? (backend / frontend / cms)"_
  - `backend` → `cetl-gear/gi-2.0-backend`
  - `frontend` → `cetl-gear/gi-2.0-frontend`
  - `cms` → `cetl-gear/gi-2.0-cms`
- **Base Branch**: `develop` (Do NOT ask the user to confirm the target branch. Skip confirmation and proceed directly.)
- **Reviewer**: `WingTSUI-HKU`
- **Draft**: `false`
- **Assignee**: `ctchan-hku`

### PR Creation Execution

Write the body to a temp file first to avoid shell escaping issues on Windows/PowerShell.

```powershell
$body | Out-File -FilePath "$env:TEMP\pr-body.txt" -Encoding utf8

& "C:\Program Files\GitHub CLI\gh.exe" pr create `
  --repo "cetl-gear/<repo>" `
  --base "develop" `
  --head "<head_branch>" `
  --title "<generated_title>" `
  --body-file "$env:TEMP\pr-body.txt" `
  --assignee "<gh_user>" `
  --reviewer "WingTSUI-HKU" `
  --draft=false
```
