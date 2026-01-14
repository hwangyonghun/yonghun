@echo off
setlocal

echo ========================================================
echo        Veritas Guard FIX & DEPLOY Tool V2
echo ========================================================
echo.

cd /d "C:\Users\User\.gemini\antigravity\scratch\yonghun"

:: 1. Initialize Git if missing
if not exist .git (
    echo [INFO] Initializing Git repository...
    git init
)

:: 2. Configure Identity (Critical for first-time git users)
git config user.email "deploy@veritas.com"
git config user.name "Veritas Deployer"

:: 3. Reset and prepare branch 'main'
echo [INFO] Preparing branch...
git checkout -B main

:: 4. Add Remote
git remote remove origin 2>nul
git remote add origin https://github.com/hwangyonghun/yonghun.git

:: 5. Stage ALL files
echo [INFO] Staging all files...
git add .

:: 6. Commit (Allow empty to ensure branch creation)
echo [INFO] Committing changes...
git commit --allow-empty -m "Force Deploy: Final UI Fixes (No Input)"

:: 7. Push
echo.
echo [IMPORTANT] Pushing to GitHub...
echo.
git push -u origin main --force

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PUSH FAILED AGAIN.
    echo.
    echo Common reasons:
    echo 1. You are not logged in. (Look for a browser popup!)
    echo 2. Internet connection issues.
    echo 3. The repository URL is wrong.
    echo.
    pause
) else (
    echo.
    echo [SUCCESS] DEPLOYMENT COMPLETE!
    echo.
    echo Please wait 2 minutes for Render.com to update the site.
    echo Go to: https://yonghun15.onrender.com
    echo.
    pause
)
