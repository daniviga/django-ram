# Django Railroad Assets Manager - Agent Guidelines

This document provides coding guidelines and command references for AI coding agents working on the Django-RAM project.

## Project Overview

Django Railroad Assets Manager (django-ram) is a Django 6.0+ application for managing model railroad collections with DCC++ EX integration. The project manages rolling stock, consists, metadata, books/magazines, and provides an optional REST API for DCC control.

## Environment Setup

### Python Requirements
- Python 3.11+ (tested on 3.13, 3.14)
- Django >= 6.0
- Working directory: `ram/` (Django project root)
- Virtual environment recommended: `python3 -m venv venv && source venv/bin/activate`

### Installation
```bash
pip install -r requirements.txt           # Core dependencies
pip install -r requirements-dev.txt       # Development tools
cd ram && python manage.py migrate        # Initialize database
python manage.py createsuperuser          # Create admin user
```

### Frontend Assets
```bash
npm install                               # Install clean-css-cli, terser
```

## Project Structure

```
ram/                      # Django project root
├── ram/                 # Core settings, URLs, base models
├── portal/              # Public-facing frontend (Bootstrap 5)
├── roster/              # Rolling stock management (main app)
├── metadata/            # Manufacturers, companies, scales, decoders
├── bookshelf/           # Books and magazines
├── consist/             # Train consists (multiple locomotives)
├── repository/          # Document repository
├── driver/              # DCC++ EX API gateway (optional, disabled by default)
└── storage/             # Runtime data (SQLite DB, media, cache)
```

## Build/Lint/Test Commands

### Running the Development Server
```bash
cd ram
python manage.py runserver                # Runs on http://localhost:8000
```

### Database Management
```bash
python manage.py makemigrations           # Create new migrations
python manage.py migrate                  # Apply migrations
python manage.py showmigrations           # Show migration status
```

### Testing
```bash
# Run all tests (comprehensive test suite with 75+ tests)
python manage.py test

# Run tests for a specific app
python manage.py test roster                  # Rolling stock tests
python manage.py test metadata                # Metadata tests  
python manage.py test bookshelf               # Books/magazines tests
python manage.py test consist                 # Consist tests

# Run a specific test case class
python manage.py test roster.tests.RollingStockTestCase
python manage.py test metadata.tests.ScaleTestCase

# Run a single test method
python manage.py test roster.tests.RollingStockTestCase.test_road_number_int_extraction
python manage.py test bookshelf.tests.TocEntryTestCase.test_toc_entry_page_validation_exceeds_book

# Run with verbosity for detailed output
python manage.py test --verbosity=2

# Keep test database for inspection
python manage.py test --keepdb

# Run tests matching a pattern
python manage.py test --pattern="test_*.py"
```

### Linting and Formatting
```bash
# Run flake8 (configured in requirements-dev.txt)
flake8 .                                  # Lint entire project
flake8 roster/                            # Lint specific app
flake8 roster/models.py                   # Lint specific file

# Note: No .flake8 config exists; uses PEP 8 defaults
# Long lines use # noqa: E501 comments in settings.py

# Run black formatter with 79 character line length
black -l 79 .                             # Format entire project
black -l 79 roster/                       # Format specific app
black -l 79 roster/models.py              # Format specific file
black -l 79 --check .                     # Check formatting without changes
black -l 79 --diff .                      # Show formatting changes
```

### Admin Commands
```bash
python manage.py createsuperuser          # Create admin user
python manage.py purge_cache              # Custom: purge cache
python manage.py loaddata <fixture>       # Load sample data
```

### Debugging & Profiling
```bash
# Use pdbpp for debugging (installed via requirements-dev.txt)
import pdb; pdb.set_trace()               # Set breakpoint in code

# Use pyinstrument for profiling
python manage.py runserver --noreload     # With pyinstrument middleware
```

## Code Style Guidelines

### General Python Style
- **PEP 8 compliant** - Follow standard Python style guide
- **Line length**: 79 characters preferred; 119 acceptable for complex lines
- **Long lines**: Use `# noqa: E501` comment when necessary (see settings.py)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Blank lines**: Must not contain any whitespace (spaces or tabs)

### Import Organization
Follow Django's import style (as seen in models.py, views.py, admin.py):

```python
# 1. Standard library imports
import os
import re
from itertools import chain
from functools import reduce

# 2. Related third-party imports
from django.db import models
from django.conf import settings
from django.contrib import admin
from tinymce import models as tinymce

# 3. Local application imports
from ram.models import BaseModel, Image
from ram.utils import DeduplicatedStorage, slugify
from metadata.models import Scale, Manufacturer
```

**Key points:**
- Group imports by category with blank lines between
- Use `from module import specific` for commonly used items
- Avoid `import *`
- Use `as` for aliasing when needed (e.g., `tinymce.models as tinymce`)

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `RollingStock`, `BaseModel`)
- **Functions/methods**: `snake_case` (e.g., `get_items_per_page()`, `image_thumbnail()`)
- **Variables**: `snake_case` (e.g., `road_number`, `item_number_slug`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `BASE_DIR`, `ALLOWED_HOSTS`)
- **Private methods**: Prefix with `_` (e.g., `_internal_method()`)
- **Model Meta options**: Use `verbose_name`, `verbose_name_plural`, `ordering`

### Django Model Patterns

```python
class MyModel(BaseModel):  # Inherit from BaseModel for common fields
    # Field order: relationships first, then data fields, then metadata
    foreign_key = models.ForeignKey(OtherModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["name"]
        verbose_name = "My Model"
        verbose_name_plural = "My Models"
    
    def __str__(self):
        return self.name
    
    @property
    def computed_field(self):
        """Document properties with docstrings."""
        return self.calculate_something()
```

**Model field conventions:**
- Use `null=True, blank=True` for optional fields
- Use `help_text` for user-facing field descriptions
- Use `limit_choices_to` for filtered ForeignKey choices
- Use `related_name` for reverse relations
- Set `on_delete=models.CASCADE` explicitly
- Use `default=None` with `null=True` for nullable fields

### Admin Customization

```python
@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "custom_method")
    list_filter = ("category", "created")
    search_fields = ("name", "slug")
    autocomplete_fields = ("foreign_key",)
    readonly_fields = ("created", "updated")
    save_as = True  # Enable "Save as new" button
    
    @admin.display(description="Custom Display")
    def custom_method(self, obj):
        return format_html('<strong>{}</strong>', obj.name)
```

### Error Handling
```python
# Use Django's exception classes
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import Http404
from django.db.utils import OperationalError, ProgrammingError

# Handle database errors gracefully
try:
    config = get_site_conf()
except (OperationalError, ProgrammingError):
    config = default_config  # Provide fallback
```

### Type Hints
- **Not currently used** in this project
- Follow existing patterns without type hints unless explicitly adding them

## Django-Specific Patterns

### Using BaseModel
All major models inherit from `ram.models.BaseModel`:
```python
from ram.models import BaseModel

class MyModel(BaseModel):
    # Automatically includes: uuid, description, notes, creation_time, 
    # updated_time, published, obj_type, obj_label properties
    pass
```

### Using PublicManager
Models use `PublicManager` for filtering published items:
```python
from ram.managers import PublicManager

objects = PublicManager()  # Only returns items where published=True
```

### Image and Document Patterns
```python
from ram.models import Image, Document, PrivateDocument

class MyImage(Image):
    my_model = models.ForeignKey(MyModel, on_delete=models.CASCADE)
    # Inherits: order, image, image_thumbnail()

class MyDocument(PrivateDocument):
    my_model = models.ForeignKey(MyModel, on_delete=models.CASCADE)
    # Inherits: description, file, private, creation_time, updated_time
```

### Using DeduplicatedStorage
For media files that should be deduplicated:
```python
from ram.utils import DeduplicatedStorage

image = models.ImageField(upload_to="images/", storage=DeduplicatedStorage)
```

## Testing Practices

### Test Coverage
The project has comprehensive test coverage:
- **roster/tests.py**: RollingStock, RollingClass models (~340 lines, 19+ tests)
- **metadata/tests.py**: Scale, Manufacturer, Company, etc. (~378 lines, 29+ tests)
- **bookshelf/tests.py**: Book, Magazine, Catalog, TocEntry (~436 lines, 25+ tests)
- **consist/tests.py**: Consist, ConsistItem (~315 lines, 15+ tests)
- **ram/tests.py**: BaseModel, utility functions (~140 lines, 11+ tests)

### Writing Tests
```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from roster.models import RollingStock

class RollingStockTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create necessary related objects
        self.company = Company.objects.create(name="RGS", country="US")
        self.scale = Scale.objects.create(scale="HO", ratio="1:87", tracks=16.5)
        # ...
    
    def test_road_number_int_extraction(self):
        """Test automatic extraction of integer from road number."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="RGS-42",
            scale=self.scale,
        )
        self.assertEqual(stock.road_number_int, 42)
    
    def test_validation_error(self):
        """Test that validation errors are raised correctly."""
        with self.assertRaises(ValidationError):
            # Test validation logic
            pass
```

**Testing best practices:**
- Use descriptive test method names with `test_` prefix
- Include docstrings explaining what each test verifies
- Create necessary test data in `setUp()` method
- Test both success and failure cases
- Use `assertRaises()` for exception testing
- Test model properties, methods, and validation logic

## Git & Version Control

- Branch: `master` (main development branch)
- CI runs on push and PR to master
- Follow conventional commit messages
- No pre-commit hooks configured (consider adding)

## Additional Notes

- **Settings override**: Use `ram/local_settings.py` for local configuration
- **Debug mode**: `DEBUG = True` in settings.py (change for production)
- **Database**: SQLite by default (in `storage/db.sqlite3`)
- **Static files**: Bootstrap 5.3.8, Bootstrap Icons 1.13.1
- **Rich text**: TinyMCE for HTMLField content
- **REST API**: Disabled by default (`REST_ENABLED = False`)
- **Security**: CSP middleware enabled, secure cookies in production
