@echo off
echo Spoustim Dochazka Agent...

:: Najdi Python
where python >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set PYTHON=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    ) else (
        echo Python nenalezen. Nainstaluj Python z python.org
        pause
        exit /b 1
    )
)

:: Spust proxy server
"%PYTHON%" server.py
pause
