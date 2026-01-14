
# Deployment Workflow

This project is deployed to Render.com automatically via GitHub.
Whenever changes are pushed to the `main` branch on GitHub, Render triggers a new build.

## How to Deploy (Agent Instructions)

**Trigger:** "Deploy", "Update site", "Push changes", or modifying any file.

**Action:** You must run the following sequence using the run_command tool correctly (using `&` for path execution if needed):

```powershell
& "C:\Program Files\Git\cmd\git.exe" add .
& "C:\Program Files\Git\cmd\git.exe" commit -m "Auto Deploy: [Description of changes]"
& "C:\Program Files\Git\cmd\git.exe" push origin main
```

**Note:** If 'git' is in the path, simplified commands work, but full path is safer.

## Manual Deployment (User)

Run the `ROBUST_DEPLOY.bat` file in the project root.
