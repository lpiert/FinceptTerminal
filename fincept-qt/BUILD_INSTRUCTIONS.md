# Fincept Terminal - Qt Creator 编译指南

## 前置要求

### 必需软件
1. **Qt Creator** (推荐最新版本)
2. **Qt 6.8.3** 或更高版本
   - 组件: MSVC 2022 64-bit
   - CMake 3.27+
   - Ninja 构建系统
3. **Visual Studio 2022** (17.8+) 或 Build Tools
4. **Python 3.12+** (用于脚本支持)

### 可选但推荐
- ccache 或 sccache (加速编译)
- Git (版本控制)

---

## 方法 1: 使用 Qt Creator GUI (推荐)

### 步骤 1: 打开项目

1. 启动 **Qt Creator**
2. 点击 `文件` → `打开文件或项目...`
3. 导航到:
   ```
   d:\workspace\free\FinceptTerminal\fincept-qt\CMakeLists.txt
   ```
4. 选择 `CMakeLists.txt` 并点击打开

### 步骤 2: 配置项目

Qt Creator 会自动检测构建设置：

1. **构建系统**: CMake
2. **生成器**: Ninja
3. **CMake 配置**:
   - Build type: `Debug` 或 `Release`
   - Qt 版本: `Qt 6.8.3 MSVC2022 64bit`
   - 编译器: `Microsoft Visual C++ Compiler 2022 (amd64)`

4. 点击 `Configure Project`

### 步骤 3: 构建项目

#### 选项 A: 使用菜单
1. 点击 `构建` → `构建所有项目`
2. 或按快捷键 `Ctrl+B`

#### 选项 B: 使用工具栏
1. 点击左下角的 🔨 锤子图标
2. 确保选择了正确的构建配置 (Debug/Release)

#### 选项 C: 命令行
在 Qt Creator 底部的 "终端" 标签中运行:
```bash
cmake --build . --config Debug
```

### 步骤 4: 运行项目

1. 构建成功后，点击绿色的 ▶️ 运行按钮
2. 或按 `Ctrl+R`
3. 程序将在调试模式下启动

---

## 方法 2: 命令行编译

### 1. 设置环境变量

打开 **Developer Command Prompt for VS 2022** 或 **x64 Native Tools Command Prompt**

### 2. 配置 CMake

```bash
cd d:\workspace\free\FinceptTerminal\fincept-qt

# 创建构建目录
mkdir build\msvc2022-debug
cd build\msvc2022-debug

# 配置项目
cmake ..\.. ^
    -G Ninja ^
    -DCMAKE_BUILD_TYPE=Debug ^
    -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64" ^
    -DCMAKE_C_COMPILER=cl ^
    -DCMAKE_CXX_COMPILER=cl
```

### 3. 编译

```bash
# 使用 8 个并行任务编译
cmake --build . --config Debug -j8
```

### 4. 运行

```bash
# Debug 版本
.\Debug\FinceptTerminal.exe

# Release 版本
.\Release\FinceptTerminal.exe
```

---

## 常见问题和解决方案

### 问题 1: CMake 找不到 Qt

**错误信息**:
```
Could not find a package configuration file provided by "Qt6"
```

**解决方案**:
```bash
# 设置 Qt 路径
set CMAKE_PREFIX_PATH=C:/Qt/6.8.3/msvc2022_64

# 或在 CMake 命令中指定
cmake .. -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64"
```

### 问题 2: MSVC 版本不匹配

**错误信息**:
```
MSVC 19.38 (Visual Studio 2022 17.8) or newer required
```

**解决方案**:
1. 更新 Visual Studio 2022 到 17.8+
2. 或修改 `CMakeLists.txt` 中的版本检查（不推荐）

### 问题 3: 依赖库缺失

**解决方案**:
项目使用 FetchContent 自动下载依赖，确保网络连接正常：
- QXlsx
- QGeoView
- SingleApplication
- Qt Advanced Docking System

### 问题 4: Python 模块缺失

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
```bash
pip install backtrader akshare pandas numpy pyqt6
```

### 问题 5: 内存不足

**症状**: 编译时卡住或崩溃

**解决方案**:
```bash
# 减少并行任务数
cmake --build . --config Debug -j2

# 或增加虚拟内存
```

---

## 构建配置选项

### Debug 模式
```bash
cmake .. -DCMAKE_BUILD_TYPE=Debug
```
- 包含调试符号
- 无优化
- 适合开发和调试

### Release 模式
```bash
cmake .. -DCMAKE_BUILD_TYPE=Release
```
- 完全优化
- 无调试符号
- 适合发布

### RelWithDebInfo 模式
```bash
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
```
- 优化 + 调试符号
- 适合性能分析

---

## 清理构建

### 方法 1: Qt Creator
1. 点击 `构建` → `清理所有项目`

### 方法 2: 命令行
```bash
cd build/msvc2022-debug
ninja clean

# 或完全删除构建目录
cd ..
rmdir /s /q msvc2022-debug
```

---

## 打包发布

### Windows (CPack)

```bash
cd build/msvc2022-release
cmake --build . --target package
```

生成的安装包位于:
- `FinceptTerminal-4.0.2-win64.exe` (NSIS)
- `FinceptTerminal-4.0.2-win64.zip` (ZIP)

### macOS

```bash
cd build/macos-release
cmake --build . --target package
```

### Linux

```bash
cd build/linux-release
cmake --build . --target package
```

---

## 性能优化技巧

### 1. 启用编译缓存
```bash
# 安装 ccache
choco install ccache

# CMake 会自动检测并使用
cmake .. -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
```

### 2. 使用预编译头
项目已启用 PCH，首次编译后速度会显著提升。

### 3. 增量编译
只修改了部分文件时，使用增量编译而非完全重建。

### 4. 分布式编译
对于大型团队，考虑使用 distcc 或 Incredibuild。

---

## 验证构建

构建完成后，运行测试套件：

```bash
cd build/msvc2022-debug
ctest --output-on-failure
```

---

## 联系支持

如遇到其他问题：
1. 查看 `CMakeFiles/CMakeOutput.log`
2. 查看 `CMakeFiles/CMakeError.log`
3. 检查 Qt Creator 的 "General Messages" 面板
4. 提交 Issue 时附上完整日志

---

**最后更新**: 2026-04-20
**Qt 版本**: 6.8.3
**CMake 版本**: 3.27+
**编译器**: MSVC 2022 (19.38+)
