# 📁 Repository Structure - Industry Standard

This document explains the new industry-standard repository structure for Argus AI Gateway.

## 🏗️ **Directory Layout**

```
argus-ai-gateway/
├── 📁 src/argus/                 # Main source code
│   ├── core/                     # Core gateway logic
│   ├── filters/                  # Security filters (L1 & L2)
│   ├── llm/                      # LLM integrations
│   ├── config/                   # Configuration management
│   ├── utils/                    # Utility functions
│   └── interfaces/               # User interfaces (CLI, Web, API)
├── 📁 tests/                     # Test suite
├── 📁 docs/                      # Documentation
├── 📁 examples/                  # Usage examples
├── 📁 scripts/                   # Development scripts
├── 📁 docker/                    # Docker configuration
├── 📄 pyproject.toml             # Modern Python packaging
└── 📄 *.py (root level)          # Backward compatibility wrappers
```

## 🔄 **Backward Compatibility**

All existing scripts continue to work unchanged:
- `python cli.py` ✅
- `python app.py` ✅  
- `python gateway.py` ✅
- `from gateway import ArgusGateway` ✅

The root-level Python files are now lightweight wrappers that import from the new structure.

## 🚀 **New Features**

### **Modern Python Packaging**
- `pyproject.toml` configuration
- Installable package: `pip install -e .`
- Command-line scripts: `argus-cli`, `argus-web`

### **Professional Testing**
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Test fixtures and data management
- Run tests: `python -m pytest tests/`

### **Development Tools**
- Pre-commit hooks for code quality
- Docker containerization
- Setup script: `python scripts/setup.py`

### **Type Safety & Validation**
- Pydantic settings with validation
- Type hints throughout codebase
- Custom exception hierarchy

## 📋 **Quick Start (New Method)**

1. **Setup Development Environment**
   ```bash
   python scripts/setup.py
   ```

2. **Install as Package**
   ```bash
   pip install -e .
   ```

3. **Use New Command-Line Tools**
   ```bash
   argus-cli          # CLI interface
   argus-web          # Web interface
   ```

4. **Import as Library**
   ```python
   from argus import ArgusGateway
   gateway = ArgusGateway()
   ```

## 🔧 **Configuration**

The new structure uses Pydantic for type-safe configuration:

```python
from argus.config.settings import settings

# Access configuration
api_key = settings.openrouter_api_key
model = settings.guard_llm_model
```

Environment variables work the same way as before through `.env` file.

## 🧪 **Testing**

Run the comprehensive test suite:

```bash
# All tests
python -m pytest tests/

# Specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/

# With coverage
python -m pytest tests/ --cov=src/argus
```

## 🐳 **Docker Support**

Build and run with Docker:

```bash
# Build image
docker build -f docker/Dockerfile -t argus-gateway .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

## 📊 **Benefits of New Structure**

1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new features and components  
3. **Testing**: Comprehensive test coverage with proper fixtures
4. **DevOps**: Production-ready deployment configurations
5. **Standards**: Follows Python packaging best practices
6. **Type Safety**: Better IDE support and error catching
7. **Documentation**: Structured documentation with examples

## 🔄 **Migration Path**

**Phase 1** (Current): Backward compatibility maintained
- All existing code works unchanged
- New features available alongside old ones

**Phase 2** (Future): Gradual migration
- Update imports to use new paths
- Leverage new type safety features
- Adopt new testing patterns

**Phase 3** (Long-term): Full modernization
- Remove backward compatibility wrappers
- Pure new structure usage

This approach ensures zero disruption while providing a clear path to modern Python development practices.
