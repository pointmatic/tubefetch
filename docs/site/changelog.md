# Changelog

All notable changes to TubeFetch are documented here. For detailed release notes, see the [GitHub Releases](https://github.com/pointmatic/tubefetch/releases) page.

---

## [0.9.6] - 2026-03-07

### Added
- **Documentation Polish & SEO**: Enhanced documentation with improved navigation and discoverability
  - Added Open Graph and Twitter Card meta tags to index.html for better social media sharing
  - Created comprehensive changelog with version history
  - Added admonitions (tips, warnings, notes) throughout documentation
  - Enhanced cross-references between documentation pages
  - Added social links (GitHub, PyPI) and copyright notice to MkDocs footer

### Changed
- Improved documentation readability and user experience
- Better SEO optimization for documentation site

---

## [0.9.5] - 2026-03-07

### Added
- **Type Safety Improvements**: Full mypy strict mode compliance
  - Added type parameters to all generic types (dict, list)
  - Added complete type annotations to CLI functions
  - Added `__all__` exports to service modules
  - Installed `types-yt-dlp` stub package
  - Fixed external library type issues

### Changed
- Improved code maintainability with comprehensive type hints
- Enhanced IDE autocomplete and type checking support

---

## [0.9.4] - 2026-03-06

### Fixed
- Fixed install command formatting in error messages (removed unescaped quotes for zsh compatibility)

---

## [0.9.3] - 2026-03-05

### Added
- Comprehensive test coverage (94%)
- Enhanced error handling and classification

---

## [0.9.0] - 2026-03-01

### Added
- **Initial Release**: Core functionality for fetching YouTube content
  - Metadata extraction via yt-dlp and YouTube Data API v3
  - Multi-format transcript support (JSON, TXT, VTT, SRT)
  - Media download (video/audio)
  - Batch processing with parallel workers
  - Intelligent caching and selective re-fetching
  - Retry logic with exponential backoff (powered by gentlify)
  - Rate limiting with token bucket algorithm
  - CLI and Python library interfaces
  - Comprehensive documentation

### Features
- **Metadata**: Extract title, channel, duration, tags, upload date
- **Transcripts**: Language preference, fallback, auto-generated support
- **Media**: Configurable quality, format selection, ffmpeg integration
- **Batch**: Concurrent processing, per-video error isolation
- **Resilience**: Smart retry classification, rate limit handling
- **Output**: Structured JSON, plain text, subtitle formats

---

## Version History

For complete version history and detailed changelogs, visit:

- [GitHub Releases](https://github.com/pointmatic/tubefetch/releases)
- [PyPI Release History](https://pypi.org/project/tubefetch/#history)

---

## Upgrade Guide

### From 0.9.x to 0.9.5

No breaking changes. Type safety improvements are internal and fully backward compatible.

### From 0.8.x to 0.9.x

No breaking changes. All new features are additive with sensible defaults.

---

## Contributing

Found a bug or have a feature request? Please open an issue on [GitHub](https://github.com/pointmatic/tubefetch/issues).
