@echo off
chcp 65001 > nul
echo ===================================================
echo  LGE Europe TV M/S and Trend Multi-Agent Pipeline
echo ===================================================
echo.
"..\01. GDMI_Weekly_Sellout_Analysis-main\.agents\python\python.exe" run_pipeline.py --step all
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Multi-Agent Pipeline Execution Failed!
    pause
    exit /b %errorlevel%
)
echo.
echo ===================================================
echo  Build Success! Generated public/index.html & Executive Report
echo ===================================================
echo.
pause
