@echo off
chcp 65001 > nul
echo ===================================================
echo  LGE Europe TV M/S and Trend Dashboard Build System
echo ===================================================
echo.
echo [Step 1/2] Extracting raw data from Databook Excel...
"..\01. GDMI_Weekly_Sellout_Analysis-main\.agents\python\python.exe" extract_ms_trend.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Excel Data Extraction Failed!
    pause
    exit /b %errorlevel%
)
echo.
echo [Step 2/2] Compiling Dashboard HTML...
"..\01. GDMI_Weekly_Sellout_Analysis-main\.agents\python\python.exe" compile_dashboard.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] HTML Compilation Failed!
    pause
    exit /b %errorlevel%
)
echo.
echo ===================================================
echo  Build Success! generated public/index.html
echo ===================================================
echo.
pause
