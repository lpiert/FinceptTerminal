@echo off
echo Setting up MSVC environment...
call "C:\Program Files\Microsoft Visual Studio\18\Professional\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

echo Configuring CMake with Ninja...
cd /d D:\workspace\free\FinceptTerminal\fincept-qt

REM Clean previous build
if exist build\ninja-release rmdir /s /q build\ninja-release

cmake -S . -B build/ninja-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64" -DCMAKE_TOOLCHAIN_FILE="D:/workspace/free/vcpkg/scripts/buildsystems/vcpkg.cmake" -DVCPKG_TARGET_TRIPLET=x64-windows -DZLIB_ROOT="D:/workspace/free/vcpkg/packages/zlib_x64-windows"

if errorlevel 1 (
    echo [ERROR] CMake configuration failed
    exit /b 1
)

echo Building project...
cmake --build build/ninja-release -j8

if errorlevel 1 (
    echo [ERROR] Build failed
    exit /b 1
)

echo Build complete!
