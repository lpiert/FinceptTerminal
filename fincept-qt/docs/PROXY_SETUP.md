# 代理设置指南 - Proxy Setup Guide

## 问题说明

如果您在下载 Python 依赖包时速度很慢，可以通过设置代理来加速下载。

## 解决方案

### 方法 1: 使用 PowerShell 脚本（推荐）✨

我们提供了一个便捷的 PowerShell 脚本来管理代理设置：

```powershell
# 进入脚本目录
cd d:\workspace\free\FinceptTerminal\fincept-qt\scripts

# 查看当前代理状态
.\set-proxy.ps1

# 设置代理（以 Clash 为例）
.\set-proxy.ps1 -Proxy "http://127.0.0.1:7890"

# 清除代理设置
.\set-proxy.ps1 -Clear
```

### 方法 2: 手动设置环境变量

在 Windows 系统环境变量中添加以下变量：

1. 打开"系统属性" → "高级" → "环境变量"
2. 在"用户变量"或"系统变量"中添加：
   ```
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```
3. 重启 Fincept Terminal

### 方法 3: 临时设置（仅当前终端会话）

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
.\FinceptTerminal.exe
```

## 常见代理地址

| 代理工具 | 地址 |
|---------|------|
| **Clash** | `http://127.0.0.1:7890` |
| **V2Ray** | `http://127.0.0.1:10809` |
| **Shadowsocks** | `socks5://127.0.0.1:1080` |
| **System Default** | 自动检测 Windows 系统代理设置 |

## 代码实现

程序已自动支持代理功能。在 [PythonSetupManager.cpp](file://d:/workspace/free/FinceptTerminal/fincept-qt/src/python/PythonSetupManager.cpp#L807-L817) 中，我们会自动检测并继承系统的环境变量：

```cpp
// Proxy support: inherit system proxy environment variables
const char* proxy_vars[] = {
    "HTTP_PROXY", "HTTPS_PROXY", 
    "http_proxy", "https_proxy", 
    "NO_PROXY", "no_proxy"
};
```

## 注意事项

⚠️ **重要提示：**
1. 设置代理后，**必须重启 Fincept Terminal** 才能生效
2. 确保您的代理软件正在运行
3. 如果使用的是 SOCKS5 代理，请使用 `socks5://` 前缀
4. 代理设置会保存到用户环境变量，对所有程序生效

## 验证代理是否生效

启动 Fincept Terminal 后，观察日志输出。如果检测到代理，会显示类似信息：

```
[INFO] PythonSetup: Proxy detected: HTTP_PROXY=http://127.0.0.1:7890
[INFO] PythonSetup: Proxy detected: HTTPS_PROXY=http://127.0.0.1:7890
```

## 故障排除

### 问题 1: 设置代理后仍然很慢

**解决方案：**
- 检查代理软件是否正常运行
- 验证代理地址和端口是否正确
- 尝试更换其他代理节点

### 问题 2: 无法连接代理

**解决方案：**
```powershell
# 清除代理设置
.\set-proxy.ps1 -Clear

# 重启程序
```

### 问题 3: 某些包不需要代理

**解决方案：**
设置 `NO_PROXY` 环境变量来排除特定域名：
```powershell
$env:NO_PROXY="localhost,127.0.0.1,.example.com"
```

## 更多信息

如有问题，请查看：
- [PythonSetupManager.cpp](file://d:/workspace/free/FinceptTerminal/fincept-qt/src/python/PythonSetupManager.cpp) - 代理实现代码
- [set-proxy.ps1](file://d:/workspace/free/FinceptTerminal/fincept-qt/scripts/set-proxy.ps1) - 代理设置脚本
