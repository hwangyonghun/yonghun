@echo off
:: BatchGotAdmin
:-------------------------------------
REM  --> 권한 확인 중...
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> 관리자 권한이 없으면 요청
if '%errorlevel%' NEQ '0' (
    echo 관리자 권한을 요청합니다...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

echo [Veritas Guard AI] Hosts 설정 중...
echo.

:: 기존 설정이 있는지 확인 (중복 방지)
findstr "www.aisolute.com" C:\Windows\System32\drivers\etc\hosts >nul
if %errorlevel% == 0 (
    echo 이미 설정되어 있습니다. (www.aisolute.com -> 127.0.0.1)
) else (
    echo 127.0.0.1 www.aisolute.com >> C:\Windows\System32\drivers\etc\hosts
    echo [성공] 도메인 연결 설정이 완료되었습니다!
)

echo.
echo 이제 브라우저에서 https://www.aisolute.com 으로 접속할 수 있습니다.
echo (브라우저를 새로고침하거나 재시작해야 할 수도 있습니다.)
pause
