# 中文界面设置指南

## 当前状态

Fincept Terminal 目前**尚未内置多语言支持**。所有界面文本都是硬编码的英文。

## 解决方案

### 方案 1: 等待官方多语言支持（推荐）

我们计划在后续版本中添加完整的多语言支持，包括：
- 中文简体 (zh-CN)
- 中文繁体 (zh-TW)
- 英文 (en-US)
- 其他语言

### 方案 2: 临时解决方案 - 使用翻译工具

如果您需要中文界面，可以：

1. **截图翻译**：使用屏幕翻译工具（如有道词典、腾讯翻译君等）
2. **浏览器插件**：如果是 Web 界面，可以使用浏览器翻译功能
3. **OCR 翻译**：使用手机拍照翻译

### 方案 3: 开发者自行添加中文支持

如果您是开发者，可以按照以下步骤添加中文支持：

#### 步骤 1: 在 CMakeLists.txt 中启用 Qt Linguist

```cmake
find_package(Qt6 COMPONENTS LinguistTools REQUIRED)

# 创建翻译文件
qt6_add_translation(QM_FILES
    translations/fincept_zh_CN.ts
)

# 在编译时处理翻译文件
add_custom_target(translations DEPENDS ${QM_FILES})
add_dependencies(FinceptTerminal translations)
```

#### 步骤 2: 在主程序中加载翻译

在 `main.cpp` 中添加：

```cpp
#include <QTranslator>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    // 加载翻译
    QTranslator translator;
    QString locale = QLocale::system().name(); // 例如 "zh_CN"
    
    if (translator.load(":/translations/fincept_" + locale)) {
        app.installTranslator(&translator);
    }
    
    // ... 其余代码
}
```

#### 步骤 3: 标记可翻译字符串

将所有用户可见的字符串用 `tr()` 包裹：

```cpp
// 之前
auto* label = new QLabel("Settings");

// 之后
auto* label = new QLabel(tr("Settings"));
```

#### 步骤 4: 生成翻译文件

```bash
# 扫描源代码生成 .ts 文件
lupdate src/ -ts translations/fincept_zh_CN.ts

# 使用 Qt Linguist 编辑翻译
linguist translations/fincept_zh_CN.ts

# 编译为 .qm 文件
lrelease translations/fincept_zh_CN.ts
```

### 方案 4: 社区贡献翻译

我们欢迎社区贡献翻译！您可以：

1. Fork 项目
2. 创建 `translations/` 目录
3. 添加中文翻译文件
4. 提交 Pull Request

## 相关资源

- [Qt 国际化文档](https://doc.qt.io/qt-6/internationalization.html)
- [Qt Linguist 手册](https://doc.qt.io/qt-6/linguist-manual.html)
- [i18n 最佳实践](https://wiki.qt.io/Internationalisation_of_Qt_Applications)

## 进度跟踪

如需了解多语言支持的进展，请关注：
- GitHub Issues: 搜索 "i18n" 或 "translation"
- 项目路线图

## 反馈

如果您希望优先支持某种语言，请在 GitHub Issues 中告诉我们！
