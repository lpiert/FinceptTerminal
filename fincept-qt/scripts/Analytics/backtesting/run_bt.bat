@echo off
REM Quick launch script for Backtrader Provider
REM Usage: run_bt.bat [command]

cd /d "%~dp0"

if "%1"=="" goto menu

:run_command
python bt_engine\backtrader_provider.py %1 %2
goto end

:menu
echo.
echo Backtrader Provider - Quick Launch
echo ====================================
echo.
echo Available commands:
echo   1. Test connection
echo   2. Run debug tool
echo   3. Run test suite
echo   4. Get strategies list
echo   5. Get indicators list
echo.
echo Or provide command directly:
echo   run_bt.bat test_connection {}
echo   run_bt.bat get_strategies {}
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" python bt_engine\backtrader_provider.py test_connection {}
if "%choice%"=="2" python bt_engine\debug_backtest.py
if "%choice%"=="3" python bt_engine\test_backtrader.py
if "%choice%"=="4" python bt_engine\backtrader_provider.py get_strategies {}
if "%choice%"=="5" python bt_engine\backtrader_provider.py get_indicators {}

:end
pause
