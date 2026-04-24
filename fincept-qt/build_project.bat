@echo off
REM Fincept Terminal Build Script
REM This script helps you build the project using Qt Creator or command line

echo ========================================
echo Fincept Terminal - Build Helper
echo ========================================
echo.

REM Check if OpenSSL is installed - try multiple locations
if exist "C:\Program Files\OpenSSL-Win64" (
    echo [OK] OpenSSL found at C:\Program Files\OpenSSL-Win64
    set OPENSSL_ROOT_DIR=C:\Program Files\OpenSSL-Win64
) else if exist "C:\ProgramData\miniconda3\Library" (
    echo [OK] OpenSSL found at Miniconda3
    set OPENSSL_ROOT_DIR=C:\ProgramData\miniconda3\Library
) else if exist "C:\msys64\mingw64" (
    echo [OK] OpenSSL found at MSYS2
    set OPENSSL_ROOT_DIR=C:\msys64\mingw64
) else (
    echo [WARN] OpenSSL development files not found
    echo.
    echo OpenSSL will be downloaded automatically by CMake during configuration.
    echo Alternatively, you can install it manually from:
    echo https://slproweb.com/products/Win32OpenSSL.html
    echo.
    set OPENSSL_ROOT_DIR=
)

REM Check if Qt is installed
if exist "C:\Qt\6.8.3\msvc2022_64" (
    echo [OK] Qt 6.8.3 found
) else (
    echo [ERROR] Qt 6.8.3 not found
    echo Expected at: C:\Qt\6.8.3\msvc2022_64
    pause
    exit /b 1
)

echo.
echo Choose build method:
echo 1. Open in Qt Creator (recommended)
echo 2. Command line build
echo 3. Just configure CMake
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto qtcreator
if "%choice%"=="2" goto cmdline
if "%choice%"=="3" goto configure

echo Invalid choice
pause
exit /b 1

:qtcreator
echo.
echo Opening project in Qt Creator...
echo After Qt Creator opens:
echo   1. Click 'Configure Project'
echo   2. Press Ctrl+B to build
echo   3. Press Ctrl+R to run
echo.
start "" "C:\Qt\Tools\QtCreator\bin\qtcreator.exe" "d:\workspace\free\FinceptTerminal\fincept-qt\CMakeLists.txt"
goto end

:cmdline
echo.
echo Starting command line build...
echo This may take 10-30 minutes for first build.
echo.

cd /d "d:\workspace\free\FinceptTerminal\fincept-qt"

echo Step 1/3: Configuring CMake...

if defined OPENSSL_ROOT_DIR (
    echo Using OpenSSL from: %OPENSSL_ROOT_DIR%
    cmake -S . -B build/vs2026 ^
        -G "Visual Studio 18 2026" ^
        -A x64 ^
        -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64" ^
        -DOPENSSL_ROOT_DIR="%OPENSSL_ROOT_DIR%"
) else (
    echo OpenSSL not specified, CMake will attempt to download it automatically...
    cmake -S . -B build/vs2026 ^
        -G "Visual Studio 18 2026" ^
        -A x64 ^
        -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64"
)

if errorlevel 1 (
    echo.
    echo [ERROR] CMake configuration failed
    pause
    exit /b 1
)

echo.
echo Step 2/3: Building project...
cmake --build build/vs2026 --config Debug -j8

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo Step 3/3: Build complete!
echo Executable location: build\vs2026\Debug\FinceptTerminal.exe
echo.
set /p run="Run now? (y/n): "
if /i "%run%"=="y" (
    start "" "build\vs2026\Debug\FinceptTerminal.exe"
)
goto end

:configure
echo.
echo Configuring CMake only...
cd /d "d:\workspace\free\FinceptTerminal\fincept-qt"

cmake -S . -B build/vs2026 ^
    -G "Visual Studio 18 2026" ^
    -A x64 ^
    -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64" ^
    -DOPENSSL_ROOT_DIR="%OPENSSL_ROOT_DIR%"

if errorlevel 1 (
    echo.
    echo [ERROR] Configuration failed
) else (
    echo.
    echo [OK] Configuration successful!
    echo You can now open the project in Qt Creator or run:
    echo   cmake --build build/vs2026 --config Debug
)
goto end

:end
echo.
echo Done!
pause
