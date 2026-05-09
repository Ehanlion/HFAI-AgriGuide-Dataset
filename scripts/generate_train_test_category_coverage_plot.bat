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

".venv\Scripts\python.exe" "python\plot_train_test_category_coverage.py" %*
set EXIT_CODE=%ERRORLEVEL%
popd

exit /b %EXIT_CODE%
