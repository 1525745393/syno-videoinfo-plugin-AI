# Makefile for Syno VideoInfo Plugin
.PHONY: help test validate package clean test-unit test-integration check-health setup-config benchmark list-flows version quality-report source-list source-status source-search source-stats source-export

# 显示帮助
help:
	@echo "Syno VideoInfo Plugin 开发工具"
	@echo ""
	@echo "可用命令："
	@echo "  make help           - 显示此帮助信息"
	@echo "  make setup-config   - 创建默认配置文件"
	@echo "  make validate       - 验证所有刮削源"
	@echo "  make check-health   - 刮削源健康检查"
	@echo "  make test           - 运行所有测试"
	@echo "  make test-unit      - 运行单元测试"
	@echo "  make test-integration - 运行集成测试"
	@echo "  make test-movie     - 测试电影刮削"
	@echo "  make test-tv        - 测试电视剧刮削"
	@echo "  make debug          - 调试模式（电影）"
	@echo "  make debug-tv       - 调试模式（电视剧）"
	@echo "  make benchmark      - 性能基准测试"
	@echo "  make package        - 打包插件"
	@echo "  make clean          - 清理打包文件"
	@echo "  make list-flows     - 列出所有刮削源"
	@echo "  make version        - 显示版本号"
	@echo "  make quality-report - 生成质量报告"
	@echo ""
	@echo "源管理命令："
	@echo "  make source-list      - 列出所有源"
	@echo "  make source-status    - 显示源健康状态"
	@echo "  make source-search q=  - 搜索源 (make source-search q=jav)"
	@echo "  make source-stats     - 显示统计信息"
	@echo "  make source-export    - 导出配置"
	@echo ""

# 设置默认配置
setup-config:
	@echo "设置默认配置文件..."
	@if [ ! -f config.json ]; then \
		cp config.example.json config.json; \
		echo "创建 config.json"; \
	else \
		echo "config.json 已存在"; \
	fi
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "创建 .env"; \
	else \
		echo ".env 已存在"; \
	fi

# 验证刮削源
validate:
	@echo "验证刮削源配置..."
	python scripts/validate_flows.py

# 刮削源健康检查
check-health:
	@echo "刮削源健康检查..."
	python scripts/source_manager.py status

# 测试刮削
test-scrape:
	@echo "运行刮削测试..."
	python main.py --type movie --input "{\"title\":\"--install\"}" --limit 1

test-movie:
	@echo "测试电影刮削..."
	python main.py --type movie --input "{\"title\":\"Avatar\"}" --limit 2 --loglevel info

test-tv:
	@echo "测试电视剧刮削..."
	python main.py --type tvshow --input "{\"title\":\"Breaking Bad\"}" --limit 2 --loglevel info

# 调试模式
debug:
	@echo "调试模式（电影）..."
	python main.py --type movie --input "{\"title\":\"ABC-123\"}" --limit 1 --loglevel debug

debug-tv:
	@echo "调试模式（电视剧）..."
	python main.py --type tvshow --input "{\"title\":\"The Office\"}" --limit 1 --loglevel debug

# 性能基准测试
benchmark:
	@echo "运行性能基准测试..."
	@python -c "
import asyncio
import time
import sys
sys.path.insert(0, '.')

print('=' * 80)
print('性能基准测试')
print('=' * 80)
print()
print('正在测试配置系统...')
start = time.time()
from scraper.config import get_config
config = get_config()
print(f'  配置系统: {(time.time() - start) * 1000:.2f}ms')
print()
print('正在测试质量系统...')
start = time.time()
from scraper.quality import DataQualityChecker
checker = DataQualityChecker()
print(f'  质量系统: {(time.time() - start) * 1000:.2f}ms')
print()
print('正在测试性能系统...')
start = time.time()
from scraper.performance import PerformanceMonitor
monitor = PerformanceMonitor()
print(f'  性能系统: {(time.time() - start) * 1000:.2f}ms')
print()
print('正在测试评分系统...')
start = time.time()
from scraper.ranking import SourceRanking
ranking = SourceRanking()
print(f'  评分系统: {(time.time() - start) * 1000:.2f}ms')
print()
print('=' * 80)
print('所有系统测试完成！')
print('=' * 80)
"

# 打包插件
package:
	@echo "检查 git 标签..."
	@if ! git describe --tags --match v[0-9]* >/dev/null 2>&1; then \
		echo "错误: 请先创建 git 标签（例如 git tag v1.4.5）"; \
		exit 1; \
	fi
	@echo "打包插件..."
	python setup.py sdist --formats=zip
	@echo ""
	@echo "完成！打包文件在 dist/ 目录"
	@ls -lh dist/

# 清理
clean:
	@echo "清理..."
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf .cache/
	rm -f scraper.log
	rm -f benchmark_results.json
	rm -f source_config.json
	find . -name "*.pyc" -delete
	@echo "清理完成"

# 安装测试
install-test:
	@echo "测试安装..."
	python main.py --type movie --input "{\"title\":\"--install\"}" --limit 1
	@echo "安装测试完成"

# 列出所有刮削源
list-flows:
	@echo "电影刮削源："
	@ls -1 scrapeflows/*_movie.json 2>/dev/null | sort || echo "无电影刮削源"
	@echo ""
	@echo "电视剧刮削源："
	@ls -1 scrapeflows/*_tvshow.json 2>/dev/null | sort || echo "无电视剧刮削源"
	@echo ""
	@echo "总计："
	@ls -1 scrapeflows/*.json 2>/dev/null | wc -l

# 显示版本
version:
	@python -c "from version import version; print(version())"

# 单元测试
test-unit:
	@echo "运行单元测试..."
	@python -m pytest tests/test_utils.py -v 2>/dev/null || \
	python -m unittest discover -s tests -p "test_*.py" -v

# 集成测试
test-integration:
	@echo "运行集成测试..."
	@python -m pytest tests/test_integration.py -v 2>/dev/null || \
	python -m unittest tests.test_integration -v

# 刮削源测试
test-scrapeflows:
	@echo "运行刮削源测试..."
	@python -m pytest tests/test_scrapeflows.py -v 2>/dev/null || \
	python -m unittest tests.test_scrapeflows -v

# 所有测试
test: test-unit test-integration test-scrapeflows
	@echo ""
	@echo "✅ 所有测试完成！"

# 质量报告
quality-report:
	@echo "生成质量报告..."
	@python -c "
import sys
sys.path.insert(0, '.')

print('=' * 80)
print('Syno VideoInfo 质量报告')
print('=' * 80)
print()
print('已安装的质量工具：')
print('  - scraper.config.ConfigManager - 配置管理系统')
print('  - scraper.ranking.SourceRanking - 刮削源评分系统')
print('  - scraper.quality.DataQualityChecker - 数据质量评估')
print('  - scraper.performance.PerformanceMonitor - 性能监控')
print('  - scraper.logger.LogManager - 日志管理')
print('  - scraper.monitor.SourceMonitor - 源监控系统')
print('  - scraper.priority_manager.PriorityManager - 优先级管理')
print()
print('可用的测试命令：')
print('  - make test-unit - 单元测试')
print('  - make test-integration - 集成测试')
print('  - make test-scrapeflows - 刮削源测试')
print('  - make benchmark - 性能基准测试')
print('  - make validate - 刮削源验证')
print('  - make check-health - 健康检查')
print()
print('源管理命令：')
print('  - make source-list - 列出所有源')
print('  - make source-status - 显示源健康状态')
print('  - make source-stats - 显示统计信息')
print()
print('=' * 80)
"

# 源管理命令
source-list:
	@echo "刮削源列表..."
	python scripts/source_manager.py list

source-status:
	@echo "源健康状态..."
	python scripts/source_manager.py status

source-search:
	@if [ "$(q)" = "" ]; then \
		echo "请提供搜索词，例如：make source-search q=jav"; \
	else \
		echo "搜索源：$(q)"; \
		python scripts/source_manager.py search "$(q)"; \
	fi

source-stats:
	@echo "源统计信息..."
	python scripts/source_manager.py stats

source-export:
	@echo "导出配置..."
	python scripts/source_manager.py export
