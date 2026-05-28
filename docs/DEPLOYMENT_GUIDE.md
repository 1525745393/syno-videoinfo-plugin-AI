# 🚀 源管理系统 - 部署指南

本文档详细介绍如何部署源管理系统。

---

## 📋 部署选项

### 选项1：使用升级脚本（推荐）

最简单的方式是运行自动升级脚本：

```bash
# 运行升级脚本
python upgrade_source_management.py

# 按照提示操作
```

---

### 选项2：手动部署

#### 步骤1：验证文件

确保以下文件存在：
```
source_groups.json          # 源分组配置
scraper/monitor.py          # 健康监控
scraper/persistence.py      # 持久化存储
scraper/source_management.py # 统一管理
scraper/priority_manager.py  # 优先级管理
scraper/source_manager.py   # 源分组管理
scraper/test_suite.py       # 测试套件
scraper/scraper_enhanced.py  # 增强版刮削器
configserver/server_enhanced.py # 增强版服务器
configserver/templates/source_management.html # UI
scripts/source_manager.py   # CLI工具
scripts/demo_source_management.py # 演示脚本
```

#### 步骤2：创建源数据目录

```bash
# 创建数据目录（如果不存在）
mkdir -p source_data
```

#### 步骤3：选择升级策略

#### A. 完全替换（完整功能）

```bash
# 备份原文件
cp scraper/scraper.py scraper/scraper.py.backup
cp configserver/server.py configserver/server.py.backup
cp main.py main.py.backup

# 替换为增强版
cp scraper/scraper_enhanced.py scraper/scraper.py
cp configserver/server_enhanced.py configserver/server.py
cp main_enhanced.py main.py
```

#### B. 部分替换（保持兼容）

只更新 `__init__.py`，其他保持不变：
```python
# scraper/__init__.py 已自动更新
# 它会优先使用 enhanced 版本，如果不可用回退到原版
```

#### 步骤4：验证部署

```bash
# 1. 运行测试
python -m unittest tests.test_persistence tests.test_source_management -v

# 2. 运行演示
python scripts/demo_source_management.py

# 3. 检查CLI
python scripts/source_manager.py list
```

---

## 🎯 验证清单

部署后运行以下检查：

- [ ] 源分组配置 `source_groups.json` 存在
- [ ] 源数据目录 `source_data/` 可写入
- [ ] 可以列出所有源
- [ ] 可以记录刮削
- [ ] 持久化存储正常工作
- [ ] 单元测试通过
- [ ] 配置服务器可以启动
- [ ] Web UI可以访问（如果使用）

---

## 📊 快速测试

运行这个快速测试：

```bash
# 运行完整演示
python scripts/demo_source_management.py

# 查看源状态
python scripts/source_manager.py status

# 查看统计
python scripts/source_manager.py stats

# 查看历史
python scripts/source_manager.py history

# 保存数据
python scripts/source_manager.py save
```

---

## 🔧 配置选项

### 基本配置

无需特殊配置，系统会使用默认设置。

### 高级配置

创建 `config.json`（可选）：

```json
{
  "source_management": {
    "enabled": true,
    "auto_save": true,
    "save_interval": 300,
    "history_retention_days": 30,
    "auto_adjust_priority": true
  }
}
```

---

## 🌐 Web界面

如果部署了增强版服务器，可以：

```bash
# 启动配置服务器
cd configserver
python server.py
```

访问：
- 主界面：`http://localhost:5125/`
- 源管理：`http://localhost:5125/sourcemgmt`

---

## 📚 使用指南

部署后参考这些文档：

- [`SOURCE_MANAGEMENT_USAGE.md`](./SOURCE_MANAGEMENT_USAGE.md) - 详细使用指南
- [`IMPLEMENTATION_COMPLETE.md`](./IMPLEMENTATION_COMPLETE.md) - 完整功能总结
- [`UNIMPLEMENTED_TASKS.md`](./UNIMPLEMENTED_TASKS.md) - 可选的额外任务

---

## ⚠️ 回滚方法

如果需要回滚：

```bash
# 恢复备份文件
cp scraper/scraper.py.backup scraper/scraper.py
cp configserver/server.py.backup configserver/server.py
cp main.py.backup main.py
```

---

## 🎉 完成检查

完成部署后，您应该拥有：

- ✅ 完整的源管理系统
- ✅ 持久化存储
- ✅ CLI管理工具
- ✅ Web界面（可选）
- ✅ 完整的测试覆盖

---

**享受您的源管理系统吧！** 🎊
