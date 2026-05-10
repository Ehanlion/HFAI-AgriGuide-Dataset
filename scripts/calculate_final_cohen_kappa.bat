@echo off
setlocal

pushd "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    call "scripts\install-deps.bat"
    if errorlevel 1 (
        set EXIT_CODE=%ERRORLEVEL%
        popd
        exit /b %EXIT_CODE%
    )
)

".venv\Scripts\python.exe" "python\calculate_final_cohen_kappa.py" %*
set EXIT_CODE=%ERRORLEVEL%
popd

exit /b %EXIT_CODE%
