@echo off
setlocal

pushd "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    python -m venv ".venv"
    if errorlevel 1 (
        set EXIT_CODE=%ERRORLEVEL%
        popd
        exit /b %EXIT_CODE%
    )
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    set EXIT_CODE=%ERRORLEVEL%
    popd
    exit /b %EXIT_CODE%
)

".venv\Scripts\python.exe" -m pip install -r "deps\requirements.txt"
set EXIT_CODE=%ERRORLEVEL%

popd
exit /b %EXIT_CODE%
