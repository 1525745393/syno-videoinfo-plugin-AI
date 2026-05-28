# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive UI overhaul with modern tab-based interface
- Dashboard with performance statistics and health monitoring
- Dark/Light theme toggle with persistent user preference
- Source search and filtering capabilities
- Batch action support for source management
- Configuration export/import functionality
- Real-time performance trend visualization
- Source health status indicators (healthy/warning/error)

### Enhanced
- Improved error handling and logging
- Enhanced configuration management system
- Better performance monitoring and caching
- Comprehensive data quality assessment
- Advanced scoring and ranking system
- Complete documentation system

### Documentation
- Complete configuration guide (CONFIGURATION.md)
- UI optimization and upgrade guides
- Quality improvement documentation
- Testing and health check guides
- Development guidelines

## [1.4.5] - 2024-XX-XX

### Added
- **Multiple New Scraping Sources** (based on mdcx project):
  - airav_movie (Airav CC)
  - avsex_movie, avsox_movie, cableav_movie
  - cnmdb_movie (Chinese Movie Database)
  - dahlia_movie (Dahlia AV)
  - fc2club_movie, fc2ppvdb_movie
  - freejavbt_movie
  - getchu_dl_movie, getchu_dmm_movie
  - guochan_movie (Chinese Domestic Content)
  - hdouban_movie, hscangku_movie
  - iqqtv_movie, love6_movie, lulubar_movie
  - madouqu_movie, mdtv_movie, mmtv_movie
  - mywife_movie, official_movie
  - theporndb_movie

### Features
- **Configuration Management**:
  - JSON/YAML configuration support
  - Environment variable overrides
  - Type-safe configuration objects
  - Configuration validation and merging

- **Performance Optimization**:
  - LRU cache with TTL support
  - Connection pooling
  - Rate limiting
  - Performance benchmarking tools

- **Quality System**:
  - Data completeness scoring
  - Format validation
  - Garbled text detection
  - Multi-dimensional quality assessment

- **Monitoring & Ranking**:
  - Source success rate tracking
  - Response time monitoring
  - Stability scoring
  - Historical performance analysis

- **Testing Framework**:
  - Unit tests for utilities
  - Integration tests for scraping flows
  - Real scraping tests with quality assessment
  - Advanced scraping integration tests

- **Health Check System**:
  - Source validity verification
  - Required field checking
  - JSON format validation
  - Accessibility testing

### Bug Fixes
- Fixed XPath expressions in JSON configuration
- Corrected JSON parsing issues in scrape flows
- Fixed validation script path errors
- Resolved Makefile target conflicts

### Dependencies
- Updated Python version requirement to 3.6+
- Added optional YAML support (PyYAML>=5.0)
- Added development dependencies (pytest, black, flake8)

## [1.4.4] - Previous Release

### Known Issues
- Limited scraping sources
- Basic configuration interface
- No performance monitoring
- Manual version management

---

## Version History

- [1.4.5](#145) - Current major update with extensive feature additions
- [1.4.4](#144) - Previous stable release
- [1.4.3](#143) - Earlier releases
- [1.0.0](#100) - Initial release

[Unreleased]: https://github.com/C5H12O5/syno-videoinfo-plugin/compare/v1.4.5...HEAD
[1.4.5]: https://github.com/C5H12O5/syno-videoinfo-plugin/releases/tag/v1.4.5
[1.4.4]: https://github.com/C5H12O5/syno-videoinfo-plugin/releases/tag/v1.4.4
[1.4.3]: https://github.com/C5H12O5/syno-videoinfo-plugin/releases/tag/v1.4.3
[1.0.0]: https://github.com/C5H12O5/syno-videoinfo-plugin/releases/tag/v1.0.0
