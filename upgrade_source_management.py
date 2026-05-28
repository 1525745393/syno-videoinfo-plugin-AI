#!/usr/bin/env python3
"""
Source Management System - Upgrade Script
"""
import os
import sys
import shutil
from pathlib import Path


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def confirm_action(prompt):
    response = input(f"{prompt} [y/N] ").lower().strip()
    return response == 'y'


def backup_file(filepath):
    backup_path = str(filepath) + ".backup"
    if filepath.exists():
        shutil.copy2(filepath, backup_path)
        print(f"  ✅ 备份已创建: {backup_path}")


def upgrade_scraper():
    """Upgrade the main scraper to use source management."""
    print_header("升级刮削器")
    
    base_dir = Path(__file__).resolve().parent
    scraper_dir = base_dir / "scraper"
    
    # Backup original
    backup_file(scraper_dir / "scraper.py")
    
    # Replace with enhanced version
    enhanced_file = scraper_dir / "scraper_enhanced.py"
    target_file = scraper_dir / "scraper.py"
    
    if enhanced_file.exists():
        shutil.copy2(enhanced_file, target_file)
        print(f"  ✅ 刮削器已更新")
    else:
        print(f"  ⚠️  找不到 enhanced 文件，跳过")


def upgrade_configserver():
    """Upgrade the configuration server."""
    print_header("升级配置服务器")
    
    base_dir = Path(__file__).resolve().parent
    config_dir = base_dir / "configserver"
    
    # Backup original
    backup_file(config_dir / "server.py")
    
    # Replace with enhanced version
    enhanced_file = config_dir / "server_enhanced.py"
    target_file = config_dir / "server.py"
    
    if enhanced_file.exists():
        shutil.copy2(enhanced_file, target_file)
        print(f"  ✅ 配置服务器已更新")
    else:
        print(f"  ⚠️  找不到 enhanced 文件，跳过")


def upgrade_main():
    """Upgrade the main entry point."""
    print_header("升级主入口")
    
    base_dir = Path(__file__).resolve().parent
    
    # Backup original
    backup_file(base_dir / "main.py")
    
    # Replace with enhanced version
    enhanced_file = base_dir / "main_enhanced.py"
    target_file = base_dir / "main.py"
    
    if enhanced_file.exists():
        shutil.copy2(enhanced_file, target_file)
        print(f"  ✅ 主入口已更新")
    else:
        print(f"  ⚠️  找不到 enhanced 文件，跳过")


def verify_files():
    """Verify that all required files exist."""
    print_header("验证文件")
    
    base_dir = Path(__file__).resolve().parent
    
    required_files = [
        "source_groups.json",
        "scraper/monitor.py",
        "scraper/persistence.py",
        "scraper/source_management.py",
        "scraper/priority_manager.py",
        "scraper/source_manager.py",
        "configserver/templates/source_management.html",
    ]
    
    all_exist = True
    for filepath in required_files:
        full_path = base_dir / filepath
        if full_path.exists():
            print(f"  ✅ {filepath}")
        else:
            print(f"  ❌ {filepath} - 缺失")
            all_exist = False
    
    return all_exist


def check_source_data():
    """Check if source data directory exists."""
    base_dir = Path(__file__).resolve().parent
    source_data_dir = base_dir / "source_data"
    
    if not source_data_dir.exists():
        print(f"  🔄 创建源数据目录: {source_data_dir}")
        source_data_dir.mkdir(parents=True, exist_ok=True)


def run_tests():
    """Run tests to verify the installation."""
    print_header("运行测试")
    
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    
    try:
        print("  运行单元测试...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "unittest", 
             "tests.test_persistence", "tests.test_source_management", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✅ 所有测试通过！")
        else:
            print(f"  ⚠️  有测试失败\n{result.stderr}")
            
    except Exception as e:
        print(f"  ⚠️  无法运行测试: {e}")


def print_quickstart():
    """Print quickstart guide."""
    print_header("快速开始")
    print("""
🎉 升级完成！现在您可以：

1. 查看源管理功能：
   python scripts/source_manager.py list
   python scripts/source_manager.py status
   python scripts/source_manager.py history

2. 运行演示：
   python scripts/demo_source_management.py

3. 启动Web界面：
   cd configserver && python server.py
   # 然后访问: http://localhost:5125/sourcemgmt

4. 运行测试：
   python -m unittest tests.test_persistence tests.test_source_management -v

5. 查看文档：
   docs/IMPLEMENTATION_COMPLETE.md - 完整总结
   docs/SOURCE_MANAGEMENT_USAGE.md - 使用指南
""")


def main():
    print_header("源管理系统 - 升级脚本")
    print("\n此脚本将帮您把源管理系统集成到现有项目中。\n")
    
    if not confirm_action("是否继续？"):
        print("操作取消。")
        return 0
    
    # Verify files
    if not verify_files():
        print("\n⚠️  缺失必要文件！请确保所有新模块都已安装。")
        return 1
    
    # Backup and upgrade
    if confirm_action("是否升级刮削器？"):
        upgrade_scraper()
    
    if confirm_action("是否升级配置服务器？"):
        upgrade_configserver()
    
    if confirm_action("是否升级主入口？"):
        upgrade_main()
    
    # Check source data dir
    check_source_data()
    
    # Run tests
    if confirm_action("是否运行验证测试？"):
        run_tests()
    
    # Print success
    print_quickstart()
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
        sys.exit(1)
