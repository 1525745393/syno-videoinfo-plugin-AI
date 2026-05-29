#!/usr/bin/env python3
"""
COMPLETE INTEGRATION SCRIPT
Integrates source management system fully into the project.
"""
import sys
import shutil
import time
from pathlib import Path


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def backup_file(filepath):
    backup_path = str(filepath) + ".backup." + str(int(time.time()))
    if filepath.exists():
        shutil.copy2(filepath, backup_path)
        print(f"  ✅ 备份已创建: {backup_path}")
        return backup_path
    return None


def replace_file(source, target):
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        print(f"  ❌ 源文件不存在: {source}")
        return False
    
    backup_file(target_path)
    shutil.copy2(source_path, target_path)
    print(f"  ✅ 文件已更新: {target}")
    return True


def main():
    print_header("源管理系统 - 完全集成")
    print("\n此脚本将把源管理系统完全集成到项目中。\n")
    
    base_dir = Path(__file__).resolve().parent
    
    # 1. Update scraper.py
    print_header("步骤 1/4: 更新刮削器")
    if replace_file(base_dir / "scraper" / "scraper_enhanced.py",
                    base_dir / "scraper" / "scraper.py"):
        print("  ✅ 刮削器已集成源管理功能")
    
    # 2. Update server.py
    print_header("步骤 2/4: 更新配置服务器")
    if replace_file(base_dir / "configserver" / "server_enhanced.py",
                    base_dir / "configserver" / "server.py"):
        print("  ✅ 配置服务器已增强")
    
    # 3. Update main.py
    print_header("步骤 3/4: 更新主入口")
    main_enhanced = base_dir / "main_enhanced.py"
    if main_enhanced.exists():
        if replace_file(main_enhanced, base_dir / "main.py"):
            print("  ✅ 主入口已更新")
    else:
        print("  ℹ️  main_enhanced.py 不存在，跳过")
    
    # 4. Verify installation
    print_header("步骤 4/4: 验证安装")
    
    # Check if data directory exists
    data_dir = base_dir / "source_data"
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        print(f"  ✅ 创建源数据目录: {data_dir}")
    
    # Verify important files exist
    required_files = [
        "source_groups.json",
        "scraper/monitor.py",
        "scraper/persistence.py",
        "scraper/source_management.py",
        "configserver/templates/source_management.html",
    ]
    
    all_exist = True
    for f in required_files:
        if (base_dir / f).exists():
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ {f}")
            all_exist = False
    
    if all_exist:
        print("\n" + "=" * 70)
        print("  🎉 集成完成！")
        print("=" * 70)
        print("""
现在您可以：

1. 使用增强的刮削功能：
   python main.py --type movie --input \"{\\\"title\\\":\\\"--install\\\"}\" --limit 1

2. 使用源管理命令：
   make source-list
   make source-status
   make source-history

3. 运行演示：
   make source-demo

4. 启动配置服务器：
   cd configserver && python server.py
   访问: http://localhost:5125/sourcemgmt

5. 查看文档：
   docs/IMPLEMENTATION_COMPLETE.md - 完整总结
   docs/SOURCE_MANAGEMENT_USAGE.md - 使用指南
   docs/DEPLOYMENT_GUIDE.md - 部署指南

6. 运行测试：
   python -m unittest tests.test_persistence tests.test_source_management -v
""")
        return 0
    else:
        print("\n⚠️  有文件缺失，请检查您的安装！")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
        sys.exit(1)
