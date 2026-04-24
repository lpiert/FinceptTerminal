# 语言切换功能使用指南

## ✨ 功能概述

Fincept Terminal 现已支持多语言界面，包括：
- 🇺🇸 **英语 (English)** - 默认语言
- 🇨🇳 **简体中文 (Chinese Simplified)** - 新增支持
- 🔄 **自动检测** - 根据系统语言自动选择

## 📖 使用方法

### 方法 1: 通过设置界面切换（推荐）

1. **打开设置**
   - 点击主界面左上角的菜单按钮
   - 选择 "Settings"（设置）

2. **进入外观设置**
   - 在左侧导航栏点击 "Appearance"（外观）

3. **选择语言**
   - 找到 "LANGUAGE"（语言）部分
   - 在 "Interface Language"（界面语言）下拉框中选择：
     - `English` - 英语
     - `Chinese (Simplified)` - 简体中文
     - `Auto-detect` - 自动检测（跟随系统）

4. **保存设置**
   - 滚动到底部，点击 "Save Settings"（保存设置）按钮

5. **重启程序**
   - 关闭 Fincept Terminal
   - 重新启动程序
   - 界面将以新选择的语言显示

### 方法 2: 自动检测系统语言

如果选择 "Auto-detect"，程序会自动检测您的系统语言：
- Windows 系统语言为中文 → 自动使用中文界面
- Windows 系统语言为英文 → 自动使用英文界面

## 🔧 技术实现

### 架构设计

```
┌─────────────────────────────────────┐
│      main.cpp (启动时加载)          │
│  ┌───────────────────────────────┐  │
│  │ 读取用户语言偏好设置           │  │
│  │ 加载对应的 .qm 翻译文件        │  │
│  │ 安装到 QApplication            │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   SettingsScreen (用户界面)         │
│  ┌───────────────────────────────┐  │
│  │ LANGUAGE 下拉框               │  │
│  │ - English (en_US)             │  │
│  │ - Chinese (zh_CN)             │  │
│  │ - Auto-detect (auto)          │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ 保存到 SettingsRepository     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    CMakeLists.txt (构建配置)        │
│  ┌───────────────────────────────┐  │
│  │ Qt Linguist Tools             │  │
│  │ - .ts → .qm 编译              │  │
│  │ - 复制到输出目录              │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 文件结构

```
fincept-qt/
├── translations/                    # 翻译文件目录
│   ├── fincept_zh_CN.ts            # 中文翻译源文件（XML）
│   └── fincept_zh_CN.qm            # 编译后的翻译文件（二进制）
├── src/
│   ├── app/
│   │   └── main.cpp                # 翻译加载逻辑
│   └── screens/settings/
│       ├── SettingsScreen.h        # 语言选择 UI 声明
│       └── SettingsScreen.cpp      # 语言选择 UI 实现
└── CMakeLists.txt                  # Qt Linguist 配置
```

### 关键代码位置

1. **CMakeLists.txt** (第 138-147 行)
   ```cmake
   find_package(Qt6 QUIET COMPONENTS LinguistTools)
   if(Qt6LinguistTools_FOUND)
       set(FINCEPT_HAS_I18N TRUE)
   endif()
   ```

2. **main.cpp** (第 93-113 行)
   ```cpp
   // Load translations (i18n)
   static QTranslator translator;
   QString lang = settings_repo.get("appearance.language", "auto").value();
   if (lang == "auto") {
       lang = QLocale::system().name();
   }
   const QString qm_path = ... + "/translations/fincept_" + lang + ".qm";
   if (QFile::exists(qm_path) && translator.load(qm_path)) {
       app.installTranslator(&translator);
   }
   ```

3. **SettingsScreen.cpp** (第 490-506 行)
   ```cpp
   // LANGUAGE section
   app_language_ = new QComboBox;
   app_language_->addItem(tr("English"), "en_US");
   app_language_->addItem(tr("Chinese (Simplified)"), "zh_CN");
   app_language_->addItem("Auto-detect", "auto");
   ```

## 🛠️ 开发者指南

### 添加新的翻译字符串

1. **在源代码中标记可翻译字符串**
   ```cpp
   // 之前
   auto* label = new QLabel("Settings");
   
   // 之后
   auto* label = new QLabel(tr("Settings"));
   ```

2. **更新翻译文件**
   ```bash
   # 扫描源代码生成 .ts 文件
   cmake --build build/Desktop_Qt_6_8_3_MSVC2022_64bit-Debug --target update_translations
   
   # 或使用 lupdate 命令
   lupdate src/ -ts translations/fincept_zh_CN.ts
   ```

3. **编辑翻译**
   - 使用 Qt Linguist 工具打开 .ts 文件
   - 或使用文本编辑器直接编辑 XML

4. **编译翻译文件**
   ```bash
   lrelease translations/fincept_zh_CN.ts -qm build/.../fincept_zh_CN.qm
   ```

### 添加新语言

1. **创建新的翻译文件**
   ```bash
   cp translations/fincept_zh_CN.ts translations/fincept_ja_JP.ts
   ```

2. **在 CMakeLists.txt 中添加**
   ```cmake
   set(TRANSLATION_FILES
       "${CMAKE_CURRENT_SOURCE_DIR}/translations/fincept_zh_CN.ts"
       "${CMAKE_CURRENT_SOURCE_DIR}/translations/fincept_ja_JP.ts"  # 新增
   )
   ```

3. **在 SettingsScreen.cpp 中添加选项**
   ```cpp
   app_language_->addItem("日本語 (Japanese)", "ja_JP");
   ```

4. **翻译并编译**
   ```bash
   lrelease translations/fincept_ja_JP.ts
   ```

## 📝 当前翻译覆盖范围

### 已翻译的部分
- ✅ 设置界面导航菜单（13 个选项）
- ✅ 外观设置（字体、主题、界面）
- ✅ 语言选择部分
- ✅ 部分常用标签和按钮

### 待翻译的部分
- ⏳ 凭证管理界面
- ⏳ 通知设置界面
- ⏳ 存储与缓存界面
- ⏳ 数据源配置
- ⏳ LLM 配置界面
- ⏳ 其他功能界面

**总计**: 约 38 个字符串已翻译，预计完整界面需要 500+ 字符串。

## 🐛 故障排除

### 问题 1: 切换语言后没有变化

**解决方案**:
1. 确认已点击 "Save Settings" 按钮
2. **必须重启程序**才能生效
3. 检查日志中是否有 "Language loaded: zh_CN" 信息

### 问题 2: 翻译文件未找到

**错误信息**: `Translation not found for 'zh_CN', using English`

**解决方案**:
1. 确认翻译文件存在：
   ```
   build/Desktop_Qt_6_8_3_MSVC2022_64bit-Debug/Debug/translations/fincept_zh_CN.qm
   ```
2. 重新编译翻译文件：
   ```bash
   lrelease translations/fincept_zh_CN.ts
   ```
3. 重新编译项目

### 问题 3: 部分界面仍显示英文

**原因**: 该部分的字符串尚未标记为可翻译（缺少 `tr()` 包裹）

**解决方案**:
1. 找到对应的源代码文件
2. 将硬编码字符串用 `tr()` 包裹
3. 重新扫描和编译翻译文件
4. 重新编译项目

## 🚀 未来计划

- [ ] 完成所有界面的中文翻译
- [ ] 添加繁体中文支持 (zh_TW)
- [ ] 添加日语支持 (ja_JP)
- [ ] 添加韩语支持 (ko_KR)
- [ ] 实现运行时语言切换（无需重启）
- [ ] 提供在线翻译贡献平台

## 📞 反馈与支持

如果您发现翻译错误或希望改进翻译质量，请：
1. 提交 GitHub Issue
2. 或直接修改 `translations/fincept_zh_CN.ts` 并提交 Pull Request

---

**版本**: v4.0.2  
**最后更新**: 2026-04-22  
**维护者**: Fincept Terminal Team
