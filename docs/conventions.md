# Project Conventions

This document outlines the coding standards, naming conventions, and organizational principles for the JUNO Automation Engine project.

## Naming Conventions

### Files and Directories
- **snake_case** for all file and directory names
  - Examples: `juno_engine.py`, `data_loader.py`, `intent_config.json`
  - Avoid: `juno-engine.py`, `JunoEngine.py`, `intent-config.json`

### Python Code
- **Classes**: PascalCase (e.g., `IntentClassifier`, `StateManager`)
- **Functions/Methods**: snake_case (e.g., `process_incoming_email`, `extract_order_id`)
- **Variables**: snake_case (e.g., `intent_config`, `mock_db`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `PROJECT_ROOT`, `PATHS`)

### JSON Configuration Files
- Use snake_case for file names
- Use snake_case for keys within JSON files
- Examples:
  - `intent_config.json` (not `intent-variable.json`)
  - `mock_database.json` (not `mock-database.json`)
  - `response_templates.json` (not `reponse-templates.json`)

## Directory Structure

```
FYP-ML/
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── juno_engine.py     # Main entry point
│   ├── data_loader.py      # Data loading utilities
│   ├── intent_classifier.py # ML model wrapper
│   ├── entity_extractor.py # Entity extraction logic
│   ├── state_manager.py    # State management
│   └── response_engine.py  # Response generation
├── data/                   # All data files
│   ├── raw/               # Original training data JSONs
│   └── processed/        # Processed/cleaned data (if needed)
├── config/                # Configuration files
│   ├── intent_config.json
│   ├── mock_database.json
│   └── response_templates.json
├── models/                # Trained ML models
│   ├── intent_classifier.joblib
│   └── label_encoder.joblib
├── notebooks/             # Jupyter notebooks
│   └── model_training.ipynb
├── scripts/               # Utility scripts
│   └── content_generation.py
├── docs/                  # Documentation
│   └── conventions.md
├── requirements.txt
└── README.md
```

## Code Organization Principles

### Module Separation
- Each major component should be in its own module file
- Modules should have a single, well-defined responsibility
- Use clear, descriptive module names that indicate their purpose

### Import Style
- Use absolute imports from the `src` package
- Example: `from src.data_loader import DataLoader`
- Group imports: standard library, third-party, local imports

### Documentation
- All classes and public functions should have docstrings
- Use Google-style docstrings with Args and Returns sections
- Include type hints where appropriate

### Error Handling
- Use descriptive error messages
- Handle file I/O errors gracefully
- Return appropriate default values (e.g., empty dict) when files are missing

## File Path Management

### Relative Paths
- Use `os.path.join()` for constructing file paths
- Define paths relative to `PROJECT_ROOT = "."`
- Centralize path definitions in configuration sections

### Path Structure
- Configuration files: `config/`
- Data files: `data/raw/` or `data/processed/`
- Models: `models/`
- Scripts: `scripts/`

## Code Style Guidelines

### Formatting
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters (soft limit)
- Use blank lines to separate logical sections

### Comments
- Use comments to explain "why", not "what"
- Section headers should use clear separators (e.g., `# ===== SECTION NAME =====`)
- Remove commented-out code before committing

### Function Design
- Keep functions focused on a single task
- Prefer small, composable functions over large monolithic ones
- Use descriptive function names that indicate their purpose

## Testing and Validation

### Test Cases
- Include test cases in the main script when run as `__main__`
- Test cases should cover different intent types and edge cases

### Error Messages
- Provide clear, actionable error messages
- Include file paths in error messages for debugging
- Use emoji indicators (✅, ❌, ⚠️) for visual feedback in console output

## Version Control

### Commit Messages
- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Group related changes in single commits

### File Tracking
- Include all necessary files in version control
- Exclude generated files, cache, and sensitive data
- Use `.gitignore` appropriately

## Documentation Standards

### README
- Keep README up-to-date with current project structure
- Include setup instructions and usage examples
- Document any external dependencies

### Code Comments
- Document complex logic and algorithms
- Explain non-obvious design decisions
- Keep comments concise and relevant

## Best Practices

1. **Modularity**: Keep code modular and reusable
2. **Clarity**: Write code that is easy to read and understand
3. **Consistency**: Follow established patterns throughout the project
4. **Maintainability**: Structure code for easy updates and extensions
5. **Documentation**: Document as you code, not as an afterthought

## Migration Notes

When migrating from old structure:
- Old: `Data/` → New: `data/raw/`
- Old: `Intent-Templates/` → New: `config/`
- Old: `engine.py` → New: `src/juno_engine.py`
- Old: `Model-Training.ipynb` → New: `notebooks/model_training.ipynb`
- Old: `Content-Generation-Script.py` → New: `scripts/content_generation.py`

All file references have been updated to use the new structure.

