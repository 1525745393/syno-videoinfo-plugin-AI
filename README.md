# Synology Video Info Plugin

[![GitHub Release](https://img.shields.io/github/v/release/C5H12O5/syno-videoinfo-plugin?logo=github&style=flat&color=blue)](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)
![GitHub Stars](https://img.shields.io/github/stars/C5H12O5/syno-videoinfo-plugin?logo=github&style=flat&color=yellow)
![GitHub Downloads](https://img.shields.io/github/downloads/C5H12O5/syno-videoinfo-plugin/total?logo=github&style=flat&color=green)
![Python Support](https://img.shields.io/badge/Python-3.6+-green?logo=python&style=flat&color=steelblue)
[![GitHub License](https://img.shields.io/github/license/C5H12O5/syno-videoinfo-plugin?logo=apache&style=flat&color=lightslategray)](LICENSE)

###### 📖 English / 📖 [简体中文](README.zh-CN.md)

A powerful video metadata plugin for Synology **Video Station** that enables fetching information from multiple sources beyond the default options.

## ✨ Features

### 🚀 Core Features
- **Zero Dependencies**: Pure Python implementation, no external packages required
- **73+ Scraping Sources**: Comprehensive coverage including JAV databases, movie sites, and more
- **Easy Configuration**: Web-based configuration interface with real-time preview
- **Multi-language Support**: Works with various languages and content types

### 📊 Advanced Features
- **Performance Monitoring**: Real-time statistics and health tracking
- **Quality Scoring**: Multi-dimensional data quality assessment
- **Smart Ranking**: Intelligent source prioritization based on success rate and speed
- **Configuration Management**: JSON/YAML config with environment variable support
- **Health Checks**: Automated validation of scraping sources

### 🎨 User Interface
- **Modern Dashboard**: Visual performance trends and statistics
- **Dark/Light Theme**: Customizable appearance with persistent preferences
- **Source Management**: Search, filter, and batch operations
- **Real-time Monitoring**: Live status indicators for all sources
- **Quick Actions**: Easy access to common operations

### 🛠️ Developer Features
- **Extensible Architecture**: Easy to add new scraping sources
- **JSON-based Configuration**: Declarative scrape flow definitions
- **Comprehensive Testing**: Unit, integration, and end-to-end tests
- **Detailed Documentation**: Complete guides for users and developers

## 📦 Supported Sources

### Movie Sources (73+)
- **JAV Database**: javbus, javdb, javlibrary, dmm, mgstage, fc2, fc2hub, fc2club, fc2ppvdb
- **Chinese**: douban, maoyan, mtime, cnmdb, hdouban, guochan, iqqtv, lulubar
- **International**: imdb, tmdb, allocine, daum, filmweb, watcha, letterboxd
- **Adult Content**: airav, avsex, avsox, cableav, freejavbt, getchu, kin8, madouqu, mdtv, mmtv, mywife, prestige, theporndb
- **And many more...**

### TV Show Sources
- **Chinese**: douban, maoyan, mtime
- **International**: tmdb, tvdb
- **Anime**: bangumi, myanimelist

## 🚀 Quick Start

### Installation

1. Download the latest release from [GitHub Releases](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)
2. Open **Video Station** → **Settings** → **Video Info Plugin**
3. Click **[Add]**, select the downloaded `.spk` file, and click **[OK]**

### Configuration

1. Open browser to `http://[NAS_IP]:5125`
2. Customize your scraping sources and priorities
3. Click the **Save** button (💾)
4. Return to Video Station - changes apply automatically!

### Basic Usage

```bash
# Test scraping
python main.py --type movie --input '{"title":"JAV-001"}' --limit 1

# With specific log level
python main.py --type movie --input '{"title":"FC2-PPV-1234"}' --limit 5 --loglevel debug

# TV show scraping
python main.py --type tvshow --input '{"title":"Breaking Bad"}' --limit 3
```

## 📚 Documentation

### For Users
- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [Configuration Guide](docs/CONFIGURATION.md) - Complete configuration reference
- [Quality Improvement](docs/QUALITY_IMPROVEMENT.md) - Optimize scraping results
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

### For Developers
- [Development Guide](docs/DEVELOPMENT.md) - Set up development environment
- [ScrapeFlows Guide](docs/SCRAPEFLOWS.md) - Create new scraping sources
- [Testing Guide](docs/TESTING_GUIDE.md) - Testing strategies and frameworks
- [Project Overview](docs/PROJECT_OVERVIEW.md) - Architecture and design

### UI Enhancement
- [UI Optimization Guide](docs/UI_OPTIMIZATION_GUIDE.md) - Feature suggestions
- [UI Upgrade Guide](docs/UI_UPGRADE_GUIDE.md) - New interface documentation

## 🔧 Configuration Example

```json
{
  "scraper": {
    "timeout": 30,
    "max_retries": 3,
    "max_concurrent": 5,
    "doh_enabled": true,
    "source_priorities": {
      "javdb_movie": 100,
      "javbus_movie": 90,
      "dmm_movie": 80
    }
  },
  "logging": {
    "level": "INFO",
    "file": "scraper.log"
  },
  "cache": {
    "enabled": true,
    "ttl": 3600
  },
  "quality": {
    "min_completeness": 70,
    "check_garbled": true
  }
}
```

## 📊 Dashboard Features

### Statistics
- **Total Sources**: 73+ available sources
- **Success Rate**: Real-time success rate monitoring
- **Avg Response Time**: Performance tracking
- **Data Quality Score**: Quality assessment

### Health Monitoring
- **Source Status**: Healthy/Warning/Error indicators
- **Trend Charts**: Visual performance over time
- **Recent Activity**: Activity timeline
- **Batch Operations**: Bulk source management

## 🧪 Testing

### Run All Tests
```bash
make test              # All tests
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-scrapeflows # Scrape flow validation
```

### Health Check
```bash
make health-check      # Check source health
make benchmark         # Performance benchmarks
make quality-report    # Generate quality report
```

### Manual Testing
```bash
# Test specific source
python main.py --type movie --input '{"title":"JAV-001"}' \
  --sources javbus_movie,javdb_movie --loglevel debug
```

## 🏗️ Development

### Setup
```bash
# Clone repository
git clone https://github.com/C5H12O5/syno-videoinfo-plugin.git
cd syno-videoinfo-plugin

# Install development dependencies
pip install pytest black flake8

# Set up configuration
make setup-config

# Run tests
make test
```

### Build Package
```bash
# Clean build
make clean

# Create distribution
make build

# Verify package
unzip -l dist/*.zip
```

### Add New Source
1. Create JSON file in `scrapeflows/` directory
2. Define scrape flow using declarative JSON syntax
3. Test with `python scripts/validate_flows.py`
4. Add to appropriate category in documentation

Example scrape flow:
```json
{
  "site": "example_movie",
  "type": "movie",
  "version": 1,
  "steps": [
    {
      "name": "search",
      "request": {
        "method": "GET",
        "url": "https://example.com/search?q={number}"
      }
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Plugin not installing**
   - Check DSM and Video Station version compatibility
   - Verify package integrity

2. **Configuration page not accessible**
   - Ensure service is running
   - Check firewall settings
   - Try restarting: Settings → Video Info Plugin → Test Connection

3. **Scraping fails**
   - Check network connectivity
   - Verify source is not blocked
   - Enable DNS-over-HTTPS if needed
   - Check logs for specific errors

4. **Poor data quality**
   - Enable multiple sources for redundancy
   - Adjust source priorities
   - Use quality scoring to identify issues

### Debug Mode
```bash
# Enable debug logging
python main.py --loglevel debug --type movie \
  --input '{"title":"TEST"}' --limit 1
```

### Health Check
```bash
# Run comprehensive health check
make health-check

# Check specific source
python scripts/validate_flows.py --source javbus_movie
```

## 📈 Performance Tips

1. **Prioritize Fast Sources**: Set javdb, javbus, dmm at top
2. **Enable Caching**: Reduces redundant requests
3. **Use DoH**: Bypass DNS pollution for better connectivity
4. **Limit Concurrent Requests**: Avoid rate limiting
5. **Monitor Success Rates**: Identify and disable failing sources

## 🤝 Contributing

Contributions are welcome! Please see our guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Synology for the Video Station platform
- All contributors and supporters
- [mdcx project](https://github.com/Hazard804/mdcx) for scraping source inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/C5H12O5/syno-videoinfo-plugin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/C5H12O5/syno-videoinfo-plugin/discussions)
- **Documentation**: [Wiki](https://github.com/C5H12O5/syno-videoinfo-plugin/wiki)

## 🔗 References

- [Video Station Metadata API](https://kb.synology.com/en-id/DSM/help/VideoStation/metadata)
- [Official API Documentation](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)

## 📋 File Naming Conventions

**Movies:**
```
Movie_Name (Release_Year).ext
Avatar (2009).avi
```

**TV Shows:**
```
TV_Show_Name.SXX.EYY.ext
Breaking_Bad.S01.E01.mkv
```

## 🔄 Version History

- **v1.4.5** (Current): Major update with 73+ sources, modern UI, performance monitoring
- **v1.4.4**: Previous stable release
- **v1.4.3**: Enhanced configuration
- **v1.0.0**: Initial release

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Made with ❤️ for Synology Video Station users**
