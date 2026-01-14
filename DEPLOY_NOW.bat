@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo        Toubina Global Deployment Assistant v1.4
echo ========================================================
echo.

:: --------------------------------------------------------
:: 1. Auto-detect Git in common locations
:: --------------------------------------------------------
set "GIT_PATH="

:: Check PATH first
where git >nul 2>nul
if %errorlevel% equ 0 set "GIT_PATH=git"

:: Check Common Directories
if "%GIT_PATH%"=="" (
    if exist "C:\Program Files\Git\cmd\git.exe" set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"
)
if "%GIT_PATH%"=="" (
    if exist "C:\Program Files\Git\bin\git.exe" set "GIT_PATH=C:\Program Files\Git\bin\git.exe"
)
if "%GIT_PATH%"=="" (
    if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe" set "GIT_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe"
)

if "%GIT_PATH%"=="" (
    echo [CRITICAL ERROR] Git not found on this computer.
    echo.
    echo Please install Git for Windows:
    echo 1. Go to https://git-scm.com/download/win
    echo 2. Download and install "64-bit Git for Windows Setup"
    echo 3. Run this script again.
    pause
    exit /b 1
)

echo [INFO] Using Git at: "%GIT_PATH%"

:: --------------------------------------------------------
:: 2. Configure & Prepare
:: --------------------------------------------------------
"%GIT_PATH%" config user.email "deploy@toubina.ai"
"%GIT_PATH%" config user.name "Toubina Deployer"

if not exist .gitignore (
    echo venv/ > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.db >> .gitignore
    echo .env >> .gitignore
    echo *.hwpx >> .gitignore
    echo *.bat >> .gitignore
    echo *.mp4 >> .gitignore
) else (
    findstr /C:"*.mp4" .gitignore >nul
    if errorlevel 1 echo *.mp4 >> .gitignore
)

:: --------------------------------------------------------
:: 3. Remote Configuration (Robust)
:: --------------------------------------------------------
echo.
echo [1/4] Configuring Remote Repository...
"%GIT_PATH%" remote remove origin >nul 2>nul
"%GIT_PATH%" remote add origin https://github.com/hwangyonghun/yonghun.git

:: --------------------------------------------------------
:: 4. Nuclear Fix (Reset Remote State)
:: --------------------------------------------------------
echo [2/4] Cleaning repository state...
"%GIT_PATH%" rm -r --cached . >nul 2>nul

echo [3/4] Adding all files (excluding large files)...
"%GIT_PATH%" add .
"%GIT_PATH%" add Procfile --force

echo [4/4] Committing changes...
"%GIT_PATH%" commit -m "Deploy to Render" >nul 2>nul

:: Switch to main just in case
"%GIT_PATH%" branch -M main

echo.
echo ========================================================
echo [ACTION REQUIRED] Pushing to GitHub...
echo A login window may appear. Please log in!
echo ========================================================
"%GIT_PATH%" push -u origin main --force

echo.
if %errorlevel% neq 0 (
    echo [ERROR] Push failed!
    echo Check your internet connection or GitHub permissions.
) else (
    echo [SUCCESS] Deployment successfully triggered!
    echo.
    echo Go to Dashboard: https://dashboard.render.com
    echo And watch the latest deploy. It should work now.
)
echo.
pause
