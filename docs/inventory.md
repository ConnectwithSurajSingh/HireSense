# HireSense Documentation Inventory

This document inventories all documentation files and their consolidation decisions.

## Markdown Files Inventory

### Root-Level Files (Keep as-is)

| File | Purpose | Decision |
|------|---------|----------|
| `README.md` | Project overview, setup instructions | **Keep at root** - Primary entry point |
| `CONTRIBUTING.md` | Contribution guidelines | **Keep at root** - Standard location |

### docs/ Directory Files

| File | Purpose | Decision |
|------|---------|----------|
| `README.md` | Docs overview, GitHub Pages info | **Move to `content/DOCUMENTATION.md`** |
| `DEPLOYMENT_GUIDE.md` | Deployment workflow details | **Move to `developer/DEPLOYMENT.md`** |
| `GITHUB_PAGES_SETUP.md` | GitHub Pages configuration | **Move to `developer/GITHUB_PAGES.md`** |
| `CI_CD_PIPELINE.md` | Pipeline technical details | **Move to `developer/CI_CD.md`** |
| `TESTING.md` | Test suite guide | **Move to `developer/TESTING.md`** |
| `UTILITY.md` | CLI utility commands | **Move to `content/UTILITIES.md`** |
| `QUICK_REFERENCE.md` | Quick reference card | **Archive** - Redundant with README |
| `MIGRATIONS.md` | Database migrations | **Move to `developer/MIGRATIONS.md`** |
| `SEED_USERS_TESTING.md` | Seed users testing | **Archive** - Covered in UTILITY.md |
| `SETUP_COMPLETE.md` | Setup summary | **Archive** - One-time setup doc |
| `THEME_GUIDE.md` | Tailwind theming | **Move to `developer/THEMING.md`** |

### GitHub Template Files (Keep as-is)

| File | Purpose | Decision |
|------|---------|----------|
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug report template | **Keep** - Standard location |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Feature request template | **Keep** - Standard location |

## Python Modules Inventory

### app/ Package

| Module | Has Module Docstring | Has Function Docstrings | Action |
|--------|---------------------|------------------------|--------|
| `__init__.py` | ✅ Yes | ✅ Yes | Verify complete |
| `models.py` | ✅ Yes (partial) | ✅ Yes | Verify complete |
| `auth.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `views.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `admin.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `employee.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `manager.py` | ⚠️ Check | ⚠️ Check | Add if missing |

### app/services/ Package

| Module | Has Module Docstring | Has Function Docstrings | Action |
|--------|---------------------|------------------------|--------|
| `__init__.py` | ⚠️ Check | N/A | Add if missing |
| `document_parser.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `learning_path_service.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `nlp_manager.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `project_service.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `resume_service.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `skill_service.py` | ⚠️ Check | ⚠️ Check | Add if missing |

### testing/ Package

| Module | Has Module Docstring | Has Function Docstrings | Action |
|--------|---------------------|------------------------|--------|
| `conftest.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `unit/test_*.py` (14 files) | ⚠️ Check | ⚠️ Check | Add module docstrings |
| `integration/test_*.py` (4 files) | ⚠️ Check | ⚠️ Check | Add module docstrings |
| `system/test_e2e.py` | ⚠️ Check | ⚠️ Check | Add module docstring |

### utility/ Package

| Module | Has Module Docstring | Has Function Docstrings | Action |
|--------|---------------------|------------------------|--------|
| `__init__.py` | ⚠️ Check | N/A | Add if missing |
| `seed_users.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `seed_projects.py` | ⚠️ Check | ⚠️ Check | Add if missing |
| `clear_db.py` | ⚠️ Check | ⚠️ Check | Add if missing |

### scripts/ Directory

| File | Has Docstring | Action |
|------|--------------|--------|
| `entrypoint.sh` | N/A (shell) | No action |
| `migrate.py` | ⚠️ Check | Add if missing |

## New Directory Structure

```
docs/
├── conf.py                 # Sphinx configuration (Shibuya theme)
├── index.rst               # Main Sphinx index
├── modules.rst             # API documentation
├── inventory.md            # This file
├── content/                # User-facing documentation
│   ├── DOCUMENTATION.md    # Documentation overview
│   └── UTILITIES.md        # CLI utilities guide
├── developer/              # Developer documentation
│   ├── DEPLOYMENT.md       # Deployment guide
│   ├── GITHUB_PAGES.md     # GitHub Pages setup
│   ├── CI_CD.md            # CI/CD pipeline
│   ├── TESTING.md          # Testing guide
│   ├── MIGRATIONS.md       # Database migrations
│   └── THEMING.md          # Tailwind theming
├── _archive/               # Deprecated/redundant docs
│   ├── QUICK_REFERENCE.md
│   ├── SEED_USERS_TESTING.md
│   └── SETUP_COMPLETE.md
├── sphinx/                 # Sphinx build artifacts
│   ├── _build/
│   ├── _static/
│   └── _templates/
└── guides/                 # (empty, can be removed)
```

## Sphinx Configuration Changes

### Extensions to Add
- `myst_parser` - Markdown support
- `sphinx.ext.autosummary` - Auto-generate summaries

### Theme Change
- From: `alabaster`
- To: `shibuya` (or fallback to `sphinx_rtd_theme`)

### Additional Modules for API Docs
- Add `testing` package to autodoc
- Add `utility` package to autodoc

## Requirements Consolidation

### Current State
- Single `requirements.txt` with 102 packages
- No `docs-requirements.txt` exists
- All dependencies (including Sphinx) inline

### Target Structure
```
# Core Web Framework
flask==X.X.X
...

# Database
sqlalchemy==X.X.X
psycopg2-binary==X.X.X
...

# NLP/ML
spacy==X.X.X
transformers==X.X.X
torch==X.X.X
...

# Testing
pytest==X.X.X
pytest-cov==X.X.X
...

# Documentation
sphinx>=7.0
myst-parser>=2.0
shibuya>=YYYY.MM.DD
sphinx-autodoc-typehints>=2.0
```

## Action Items

1. ✅ Create inventory (this file)
2. ⏳ Create directory structure (content/, developer/, _archive/)
3. ⏳ Move and consolidate markdown files
4. ⏳ Update Sphinx conf.py for Shibuya theme
5. ⏳ Add docstrings to all Python modules
6. ⏳ Create comment stripping script
7. ⏳ Run comment cleanup
8. ⏳ Consolidate requirements.txt
9. ⏳ Update CI/CD workflow
10. ⏳ Test and verify

---
*Generated: 2026-03-29*
