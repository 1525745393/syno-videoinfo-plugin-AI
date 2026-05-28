# 📋 未实施功能清单

本文档列出了尚未完全实施的功能和集成工作。

---

## 🎯 高优先级集成任务

### 1. ✅ 已完成的工作
- 源管理系统核心模块
- 持久化存储
- Web UI界面
- 单元测试
- CLI工具
- 演示脚本
- 文档

---

### 2. 🔄 未完全实施的内容

#### A. 主入口集成
**状态：** 部分完成（有 `scraper_enhanced.py` 但未替换旧版）
- `scraper/scraper.py` - 仍使用旧版刮削器
- `scraper/__init__.py` - 仅导出旧版功能
- `main.py` - 使用旧版入口

#### B. 配置服务器集成
**状态：** 有增强版但未启用
- `configserver/server.py` - 仍使用旧版
- 源管理UI已有但未连接到主服务器路由
- 主页面未添加源管理链接

#### C. 源管理集成到实际刮削
**状态：** 有 `scraper_enhanced.py` 但未实际使用
- 刮削记录功能未在真实刮削中启用
- 智能源选择未在生产中使用

#### D. 部署相关
- 没有一键部署脚本
- 没有升级指南
- 没有完整的验证清单

---

## 🚀 实施建议

### 方案1：最小改动（推荐）
- 在现有系统中添加源管理功能
- 保持向后兼容
- 添加可配置的开关

### 方案2：完全替换
- 用新版本替换旧版本
- 更新所有入口点
- 添加完整的迁移路径

---

## 📊 当前状态对比

| 组件 | 旧版 | 新版 | 状态 |
|------|------|------|------|
| 刮削器 | scraper.py | scraper_enhanced.py | 新版未启用 |
| 配置服务器 | server.py | server_enhanced.py | 新版未启用 |
| 源管理 | 无 | 完整实现 | 已完成 |
| Web UI | 基础界面 | 增强版 + 源管理 | 部分完成 |
| 持久化 | 无 | 完整实现 | 已完成 |

---

## ✅ 快速验证清单

运行以下命令验证现有功能：

```bash
# 运行测试
python -m unittest tests.test_persistence tests.test_source_management -v

# 运行演示
python scripts/demo_source_management.py

# 使用CLI
python scripts/source_manager.py list
python scripts/source_manager.py status
```

---

*本文档最后更新：2026-05-28*
