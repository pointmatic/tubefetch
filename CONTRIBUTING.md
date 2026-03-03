# Contributing to yt-fetch

Thank you for your interest in contributing to yt-fetch! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.14+
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/pointmatic/yt-fetch.git
cd yt-fetch

# Install development dependencies
pip install -e ".[dev,youtube-api]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yt_fetch --cov-report=term-missing

# Run specific test file
pytest tests/test_models.py

# Run integration tests (requires network)
RUN_INTEGRATION=1 pytest tests/integration/
```

### Code Quality

```bash
# Run linting
ruff check .

# Run formatting check
ruff format --check .

# Auto-format code
ruff format .
```

## Code Style

### General Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for public APIs
- Keep functions focused and single-purpose
- Prefer explicit over implicit

### License Headers

All Python source files must include the Apache-2.0 license header:

```python
# Copyright (c) 2026 Pointmatic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

### Ruff Configuration

The project uses `ruff` for linting and formatting. Configuration is in `pyproject.toml`:
- Target: Python 3.14
- Line length: 120 characters
- Selected rules: E (errors), F (pyflakes), I (isort), W (warnings)

## Pull Request Process

### Before Submitting

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Run tests and linting**:
   ```bash
   pytest
   ruff check .
   ruff format --check .
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

### Submitting a Pull Request

1. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues
   - Screenshots/examples if applicable

3. **Wait for CI checks** to pass:
   - All tests must pass
   - Code coverage should not decrease
   - Linting must pass

4. **Address review feedback** if requested

### PR Requirements

- ✅ All CI checks pass
- ✅ Tests added for new functionality
- ✅ Code follows style guidelines
- ✅ License headers present in new files
- ✅ Documentation updated if needed

## Reporting Issues

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Minimal code example

### Feature Requests

When requesting features, please include:
- Use case description
- Proposed API/interface
- Why existing functionality doesn't work
- Willingness to contribute implementation

## Development Workflow

### Project Structure

```
yt-fetch/
├── yt_fetch/           # Main package
│   ├── core/          # Core models, errors, pipeline
│   ├── services/      # External service integrations
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── docs/              # Documentation
└── .github/           # GitHub workflows
```

### Adding New Features

1. Check existing issues/PRs for similar work
2. Open an issue to discuss the feature
3. Get feedback before starting implementation
4. Follow the PR process above

### Fixing Bugs

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test now passes
4. Submit PR with test + fix

## Release Process

Releases are automated via GitHub Actions. When you push a version tag, the workflow will:
- Build the package (sdist + wheel)
- Publish to PyPI as `tubefetch`
- Create a GitHub Release with auto-generated release notes

### Steps to Release

1. **Update version numbers**:
   ```bash
   # Update version in pyproject.toml
   # Update __version__ in yt_fetch/__init__.py
   ```

2. **Update CHANGELOG.md** (optional but recommended):
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Added
   - New feature description
   
   ### Changed
   - Changed feature description
   
   ### Fixed
   - Bug fix description
   ```

3. **Commit changes**:
   ```bash
   git add pyproject.toml yt_fetch/__init__.py CHANGELOG.md
   git commit -m "Release vX.Y.Z"
   ```

4. **Create and push tag**:
   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

5. **Automated workflow**:
   - GitHub Actions builds the package
   - Publishes to PyPI (requires PyPI trusted publisher configured)
   - Creates GitHub Release with auto-generated notes from merged PRs

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### First-Time Release Setup

Before the first release, configure PyPI trusted publisher:
1. Go to https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - PyPI Project Name: `tubefetch`
   - Owner: `pointmatic`
   - Repository: `yt-fetch`
   - Workflow: `release.yml`
   - Environment: `pypi`

## Questions?

- Open an issue for questions about contributing
- Check existing issues and PRs for similar discussions
- Review the documentation in `docs/`

Thank you for contributing to yt-fetch! 🎉
