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

".venv\Scripts\python.exe" "python\merge_final_fertilizer_results.py" %*
set EXIT_CODE=%ERRORLEVEL%
popd

exit /b %EXIT_CODE%
