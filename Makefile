# Makefile for Syno VideoInfo Plugin

.PHONY: help test validate package clean test-unit test-integration check-health

# 显示帮助
help:
	@echo "Syno VideoInfo Plugin 开发工具"
	@echo ""
	@echo "可用命令："
	@echo "  make help        - 显示此帮助信息"
	@echo "  make validate    - 验证所有刮削源"
	@echo "  make check-health - 刮削源健康检查"
	@echo "  make test        - 运行所有测试"
	@echo "  make test-unit   - 运行单元测试"
	@echo "  make test-integration - 运行集成测试"
	@echo "  make test-movie  - 测试电影刮削"
	@echo "  make test-tv     - 测试电视剧刮削"
	@echo "  make package     - 打包插件"
	@echo "  make clean       - 清理打包文件"
	@echo "  make docs        - 生成文档（如果有）"
	@echo ""

# 验证刮削源
validate:
	@echo "验证刮削源配置..."
	python scripts/validate_flows.py

# 刮削源健康检查
check-health:
	@echo "刮削源健康检查..."
	python scripts/check_health.py

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

# 打包插件
package:
	@echo "检查 git 标签..."
	@if ! git describe --tags --match v[0-9]* >/dev/null 2>&1; then \
		echo "错误: 请先创建 git 标签（例如 git tag v1.0.0）"; \
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
	@ls -1 scrapeflows/*_movie.json | sort
	@echo ""
	@echo "电视剧刮削源："
	@ls -1 scrapeflows/*_tvshow.json | sort
	@echo ""
	@echo "总计："
	@ls -1 scrapeflows/*.json | wc -l

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
