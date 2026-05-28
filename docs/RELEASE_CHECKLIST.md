# Release Checklist

A comprehensive checklist for preparing a new release of the Synology Video Info Plugin.

## Pre-Release Phase

### 📋 Documentation Review

- [ ] Update CHANGELOG.md with all changes
- [ ] Review and update README.md
  - [ ] Verify installation instructions are current
  - [ ] Check all features are documented
  - [ ] Verify screenshots are up-to-date
  - [ ] Test all code examples
- [ ] Review all docs/ files for accuracy
  - [ ] CONFIGURATION.md
  - [ ] QUALITY_IMPROVEMENT.md
  - [ ] UI_UPGRADE_GUIDE.md
  - [ ] TESTING_GUIDE.md
  - [ ] HEALTH_CHECK_GUIDE.md
  - [ ] DEVELOPMENT.md
  - [ ] QUICKSTART.md
  - [ ] TROUBLESHOOTING.md
  - [ ] SCRAPEFLOWS.md
  - [ ] PROJECT_OVERVIEW.md

### 🧪 Testing

- [ ] Run all unit tests
  ```bash
  make test-unit
  ```
- [ ] Run all integration tests
  ```bash
  make test-integration
  ```
- [ ] Run scrape flow validation
  ```bash
  make test-scrapeflows
  ```
- [ ] Test scraping with real sources
  ```bash
  python main.py --type movie --input '{"title":"JAV-001"}' --limit 1
  ```
- [ ] Test configuration server
  ```bash
  python configserver/server.py
  ```
- [ ] Verify new UI (index.v2.html) if using
- [ ] Test on actual Synology NAS (if available)

### 🔍 Code Quality

- [ ] Run linting checks
  ```bash
  make lint
  ```
- [ ] Check code formatting
  ```bash
  make format-check
  ```
- [ ] Verify no hardcoded secrets or keys
- [ ] Review all new code for security issues
- [ ] Check dependency vulnerabilities
  ```bash
  pip audit  # if available
  ```

### 📦 Build & Package

- [ ] Clean previous builds
  ```bash
  make clean
  ```
- [ ] Create package
  ```bash
  make build
  ```
- [ ] Verify package contents
  ```bash
  unzip -l dist/*.zip
  ```
- [ ] Test package installation (manual if possible)
- [ ] Verify INFO file is generated correctly
- [ ] Check all required files are included

### ✅ Validation

- [ ] Validate all JSON scrape flows
  ```bash
  python scripts/validate_flows.py
  ```
- [ ] Run health checks on all sources
  ```bash
  make health-check
  ```
- [ ] Run performance benchmarks
  ```bash
  make benchmark
  ```
- [ ] Generate quality report
  ```bash
  make quality-report
  ```

## Release Phase

### 🏷️ Version Management

- [ ] Decide version number (follow semantic versioning)
  - Major version: Breaking changes
  - Minor version: New features, backward compatible
  - Patch version: Bug fixes
- [ ] Create git tag
  ```bash
  git tag -a v1.4.5 -m "Version 1.4.5 release"
  ```
- [ ] Verify tag is correct
  ```bash
  git tag -l
  git show v1.4.5
  ```
- [ ] Push tag to remote
  ```bash
  git push origin v1.4.5
  ```

### 📝 Release Notes

- [ ] Draft release notes on GitHub
- [ ] Include:
  - [ ] Version number and release date
  - [ ] Summary of changes
  - [ ] New features with descriptions
  - [ ] Bug fixes
  - [ ] Known issues
  - [ ] Upgrade instructions (if needed)
  - [ ] Download links
- [ ] Review release notes for clarity
- [ ] Add screenshots/animations if helpful
- [ ] Preview before publishing

### 🚀 Publishing

- [ ] Ensure GitHub Actions workflow is set up
  - [ ] Check .github/workflows/release.yml
  - [ ] Verify workflow permissions
  - [ ] Test workflow locally if possible
- [ ] Push tags to trigger workflow
  ```bash
  git push origin --tags
  ```
- [ ] Monitor GitHub Actions run
  - [ ] Verify build succeeds
  - [ ] Check artifact upload
  - [ ] Confirm release creation
- [ ] Verify release appears on GitHub
- [ ] Download and verify zip file

### 📢 Announcement

- [ ] Create announcement message
- [ ] Post on relevant platforms:
  - [ ] GitHub Releases page
  - [ ] Synology community forums (if applicable)
  - [ ] Reddit (r/synology, r/javadmin, etc.)
  - [ ] Other relevant communities
- [ ] Update documentation links
- [ ] Create migration guide if needed (for major updates)

## Post-Release

### 🔍 Verification

- [ ] Monitor for installation issues
- [ ] Check for error reports
- [ ] Verify download count increases
- [ ] Monitor GitHub Issues for new reports
- [ ] Check user feedback

### 🔧 Support

- [ ] Monitor release discussions
- [ ] Respond to user questions
- [ ] Document workaround for reported issues
- [ ] Plan hotfix if critical bugs found

### 📊 Metrics

- [ ] Track download statistics
- [ ] Monitor star count changes
- [ ] Review user feedback trends
- [ ] Plan next release based on feedback

### 📝 Maintenance

- [ ] Update issue templates for next release
- [ ] Create backlog for next version
- [ ] Schedule follow-up tasks
- [ ] Update development timeline

## Quick Release (Hotfix)

For urgent bug fixes:

- [ ] Create fix branch from main
  ```bash
  git checkout -b hotfix/v1.4.6
  ```
- [ ] Apply minimal fix
- [ ] Update CHANGELOG
- [ ] Run quick tests
  ```bash
  make test-quick
  ```
- [ ] Create tag and push
  ```bash
  git tag v1.4.6
  git push origin hotfix/v1.4.6
  ```
- [ ] Monitor CI/CD pipeline
- [ ] Verify release

## Rollback Plan

If critical issues found:

- [ ] Identify problematic commit(s)
- [ ] Assess rollback scope
- [ ] Create rollback plan
- [ ] Execute rollback if necessary
- [ ] Communicate with users
- [ ] Issue immediate hotfix

---

## Pre-Flight Check (Run Before Every Release)

```bash
# 1. Clean build
make clean

# 2. Run all tests
make test

# 3. Validate flows
python scripts/validate_flows.py

# 4. Build package
make build

# 5. Check package
unzip -l dist/*.zip

# 6. Quick manual test
python main.py --help

# 7. Review changes
git log --oneline --since="2 weeks ago"

# 8. Update version
# Edit version in setup.py or use git tag

# 9. Final verification
git status
```

## Notes

- Always create a backup before major releases
- Test on actual Synology hardware when possible
- Keep release notes concise but comprehensive
- Communicate changes clearly to users
- Monitor feedback after release

---

**Version**: 1.4.5  
**Last Updated**: 2024-XX-XX  
**Next Scheduled Release**: TBD
