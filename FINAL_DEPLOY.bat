@echo off
setlocal

echo ========================================================
echo        FINAL DEPLOYMENT ATTEMPT
echo ========================================================
echo.

:: 1. Find Git
set "GIT_PATH="
if exist "C:\Program Files\Git\cmd\git.exe" set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"
if "%GIT_PATH%"=="" set "GIT_PATH=git"

echo [DEBUG] Using Git: %GIT_PATH%
echo.

:: 2. Configure Output
echo [1/4] Resetting Git Config...
"%GIT_PATH%" config --local --unset credential.helper
"%GIT_PATH%" config --local credential.helper manager
"%GIT_PATH%" remote remove origin
"%GIT_PATH%" remote add origin https://github.com/hwangyonghun/yonghun.git

echo.
echo [2/4] Ensuring Content...
"%GIT_PATH%" add .
"%GIT_PATH%" commit --allow-empty -m "Deployment trigger"

echo.
echo [3/4] Pushing to GitHub...
echo.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo [IMPORTANT]
echo A browser window should open automatically for login.
echo If it does not appear, CHECK YOUR TASKBAR (Icon: GitHub or Chrome/Edge).
echo.
echo If you see a login prompt in this window instead, use it.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo.

"%GIT_PATH%" push -u origin main --force

echo.
echo ========================================================
if %errorlevel% neq 0 (
    echo [FAILURE] Still failing?
    echo Try restarting your computer or installing GitHub Desktop.
) else (
    echo [SUCCESS] Deployed successfully!
)
echo.
pause
