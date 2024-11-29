@echo off
REM This script cleans Python build artifacts in the current directory and its subdirectories.

REM Function to delete folders recursively
for /d /r %%d in (build, dist, *.egg-info, __pycache__) do (
    echo Deleting %%d
    rd /s /q "%%d"
)

REM Optionally clear *.pyc files too
echo Deleting .pyc files...
for /r %%f in (*.pyc) do (
    echo Deleting %%f
    del /f /q "%%f"
)

echo Cleanup complete.
pause
