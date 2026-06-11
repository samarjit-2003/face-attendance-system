@echo off
echo Starting Face Attendance Web Application...
echo.

:: Set the path to the virtual environment's packages
set PYTHONPATH=%~dp0.venv\Lib\site-packages

:: Run the Uvicorn server using the exact Python 3.11 installation that works
"C:\Users\SAMARJIT HALDER\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe" -m uvicorn web_app:app --reload

pause
