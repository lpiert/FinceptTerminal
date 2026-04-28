# Fincept Terminal 免费化改造 - 快速参考

## 🎯 一句话总结
**所有付费功能已解锁,通过修改2个文件+新建1个脚本实现40%改造,剩余60%按TODO清单逐步完成。**

---

## ✅ 已完成 (复制即用)

### 1. 订阅检查绕过
```cpp
// src/auth/AuthTypes.h - Line 202
bool has_paid_plan() const {
    return true;  // [FREE-MODE-STUB] All features unlocked
}
```

### 2. 无限信用点设置
```cpp
// src/auth/AuthManager.cpp - Line 201
session_.subscription.credit_balance = 999999;
session_.user_info.credit_balance = 999999;
```

### 3. 免费宏观数据聚合器
```bash
# 已创建: scripts/free_macro_aggregator.py
python free_macro_aggregator.py dashboard US  # 测试
```

---

## 🔨 待处理 (按优先级)

### 🔴 高优先级 (3小时)
1. **连接FinceptMacroPanel** → `FinceptMacroPanel.cpp`
2. **PricingScreen提示** → `PricingScreen.cpp`  
3. **Profile显示∞** → `ProfileScreen.cpp`

### 🟡 中优先级 (11小时)
4. **Reddit情感分析** → 新建 `reddit_sentiment.py`
5. **API速率限制** → 新建 `api_rate_limiter.py`
6. **DocsScreen章节** → `DocsScreen.cpp`
7. **About许可声明** → `AboutScreen.cpp`

### 🟢 低优先级 (6小时)
8. **Sentinel指南** → 新建文档
9. **配置模板** → 新建 `free_mode.ini.example`
10. **性能基准** → 新建 `benchmark_free_vs_paid.py`

---

## 📚 文档导航

| 文档 | 用途 | 行数 |
|------|------|------|
| **FREE_ALTERNATIVES_GUIDE.md** | 完整使用指南 | 398 |
| **FREE_MODE_CHECKLIST.md** | 详细改造清单 | 501 |
| **FREE_MODE_TODO.md** | TODO行动清单(含代码) | 644 |
| **FREE_MODE_SUMMARY.md** | 总结报告 | 426 |
| **FREE_MODE_QUICKREF.md** | 本文档(快速参考) | - |

**推荐阅读顺序:** SUMMARY → TODO → QUICKREF → CHECKLIST

---

## 🔧 常用命令

### 测试免费聚合器
```bash
cd fincept-qt/scripts
python free_macro_aggregator.py dashboard US
python free_macro_aggregator.py rates EU
python free_macro_aggregator.py inflation CN
```

### 编译项目
```bash
cd fincept-qt/build
cmake --build .
```

### 清理重新编译
```bash
cmake --build . --target clean
cmake --build .
```

### 运行应用
```bash
# Linux/macOS
./build/FinceptTerminal

# Windows
.\build\FinceptTerminal.exe
```

---

## 🆘 故障排除

### Q1: 编译错误 "undefined reference to has_paid_plan"
**解决:** 确认 `AuthTypes.h` 修改已保存,重新运行CMake

### Q2: 启动后仍显示付费提示
**解决:** 删除会话文件后重启
```bash
# Linux/macOS
rm ~/.config/FinceptTerminal/session.json

# Windows  
del %APPDATA%\FinceptTerminal\session.json
```

### Q3: free_macro_aggregator.py 导入错误
**解决:** 安装依赖
```bash
pip install pandas akshare
```

### Q4: Ollama连接失败
**解决:** 启动Ollama服务
```bash
ollama serve  # 保持运行
ollama pull llama3.2  # 下载模型
```

---

## 📊 进度追踪

```
总进度: ████████░░░░░░░░░░░░ 40%

✅ 核心架构: ████████████████████ 100%
🔨 功能完善: ████░░░░░░░░░░░░░░░░  20%
📝 文档优化: ██████████░░░░░░░░░░  50%
⚠️  合规检查: ████████████████░░░░  80%
```

---

## 🎯 今日目标

**如果只有1小时:**
- [ ] 完成任务1: 连接FinceptMacroPanel (30min)
- [ ] 完成任务2-3: UI提示修改 (30min)

**如果有半天:**
- [ ] 完成所有高优先级任务 (3h)
- [ ] 开始任务4: Reddit脚本 (1h)

**如果有1周:**
- [ ] 完成所有中高优先级任务 (14h)
- [ ] 端到端测试
- [ ] 收集反馈

---

## 🔗 关键链接

### API注册
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html
- Reddit: https://www.reddit.com/prefs/apps
- NewsAPI: https://newsapi.org/register
- DeepSeek: https://platform.deepseek.com
- Groq: https://console.groq.com

### 开源项目
- AKShare: https://github.com/akfamily/akshare
- Ollama: https://github.com/ollama/ollama
- QuantLib: https://github.com/lballabio/QuantLib
- Backtrader: https://github.com/mementum/backtrader

### 文档
- 上游仓库: https://github.com/Fincept-Corporation/FinceptTerminal
- AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.html

---

## 💡 技巧提示

### 快速验证免费模式
```cpp
// 在任何地方添加调试输出
LOG_INFO("FreeMode", "has_paid_plan: " + QString::number(auth.session().has_paid_plan()));
LOG_INFO("FreeMode", "credit_balance: " + QString::number(auth.session().user_info.credit_balance));
// 应输出: has_paid_plan: true, credit_balance: 999999
```

### 查看所有打桩位置
```bash
# Linux/macOS
grep -r "\[FREE-MODE" fincept-qt/src/

# Windows PowerShell
Select-String -Path "fincept-qt\src\*" -Pattern "\[FREE-MODE"
```

### 恢复到商业版
```bash
# Step 1: Git还原修改
git checkout HEAD -- src/auth/AuthTypes.h
git checkout HEAD -- src/auth/AuthManager.cpp

# Step 2: 重新编译
cd fincept-qt/build && cmake --build . --target clean && cmake --build .

# Step 3: 清除会话
rm ~/.config/FinceptTerminal/session.json
```

---

## 📞 获取帮助

**遇到问题?**
1. 查看 `FREE_MODE_TODO.md` 中的详细代码示例
2. 搜索GitHub Issues是否有类似问题
3. 在GitHub Discussions提问
4. 检查控制台日志 (`LOG_INFO` 输出)

**贡献代码?**
1. Fork仓库
2. 创建特性分支
3. 提交PR并标注 `[FREE-MODE]`
4. 等待社区审核

---

**最后更新:** 2026-04-20  
**维护者:** Community  
**版本:** v1.0-free-beta  
**许可证:** AGPL-3.0
