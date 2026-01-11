@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        Veritas Guard Force Deploy Tool (Fix)
echo ========================================================
echo.

set "GIT_PATH="
if exist "C:\Program Files\Git\cmd\git.exe" set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"
if "%GIT_PATH%"=="" set "GIT_PATH=git"

echo [1/5] Checking Git...
"%GIT_PATH%" --version
if %errorlevel% neq 0 (
    echo [ERROR] Git not found! Please install Git.
    pause
    exit /b
)

echo.
echo [2/5] Configuring Repository...
"%GIT_PATH%" init
"%GIT_PATH%" remote remove origin 2>nul
"%GIT_PATH%" remote add origin https://github.com/hwangyonghun/yonghun.git
"%GIT_PATH%" branch -M main

echo.
echo [3/5] Creating New Commit...
"%GIT_PATH%" add .
"%GIT_PATH%" commit -m "Force Deploy: Fixed previous deployment issues" 
:: If commit fails because no changes, that's fine, we continue.

echo.
echo [4/5] Pushing to GitHub...
echo.
echo ********************************************************
echo  PLEASE LOG IN IF ASKED! (Browser or Token)
echo ********************************************************
echo.
"%GIT_PATH%" push -u origin main --force

echo.
echo ========================================================
if %errorlevel% neq 0 (
    echo [ERROR] Deployment FAILED.
    echo Please check your internet or GitHub login.
) else (
    echo [SUCCESS] Deployment COMPLETE!
    echo Your code is now on GitHub. Render should start building.
)
echo.
pause
