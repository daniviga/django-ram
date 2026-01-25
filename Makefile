# Makefile for Django RAM project
# Handles frontend asset minification and common development tasks

.PHONY: help minify minify-js minify-css clean install test

# Directories
JS_SRC_DIR = ram/portal/static/js/src
JS_OUT_DIR = ram/portal/static/js
CSS_SRC_DIR = ram/portal/static/css/src
CSS_OUT_DIR = ram/portal/static/css

# Source files
JS_SOURCES = $(JS_SRC_DIR)/theme_selector.js $(JS_SRC_DIR)/tabs_selector.js $(JS_SRC_DIR)/validators.js

CSS_SOURCES = $(CSS_SRC_DIR)/main.css

# Output files
JS_OUTPUT = $(JS_OUT_DIR)/main.min.js
CSS_OUTPUT = $(CSS_OUT_DIR)/main.min.css

# Default target
help:
	@echo "Django RAM - Available Make targets:"
	@echo ""
	@echo "  make install     - Install npm dependencies (terser, clean-css-cli)"
	@echo "  make minify      - Minify both JS and CSS files"
	@echo "  make minify-js   - Minify JavaScript files only"
	@echo "  make minify-css  - Minify CSS files only"
	@echo "  make clean       - Remove minified files"
	@echo "  make watch       - Watch for changes and auto-minify (requires inotify-tools)"
	@echo "  make run         - Run Django development server"
	@echo "  make test        - Run Django test suite"
	@echo "  make lint        - Run flake8 linter"
	@echo "  make format      - Run black formatter (line length 79)"
	@echo "  make ruff-check  - Run ruff linter"
	@echo "  make ruff-format - Run ruff formatter"
	@echo "  make dump-data   - Dump database to gzipped JSON (usage: make dump-data FILE=backup.json.gz)"
	@echo "  make load-data   - Load data from fixture file (usage: make load-data FILE=backup.json.gz)"
	@echo "  make help        - Show this help message"
	@echo ""

# Install npm dependencies
install:
	@echo "Installing npm dependencies..."
	npm install
	@echo "Done! terser and clean-css-cli installed."

# Minify both JS and CSS
minify: minify-js minify-css

# Minify JavaScript
minify-js: $(JS_OUTPUT)

$(JS_OUTPUT): $(JS_SOURCES)
	@echo "Minifying JavaScript..."
	npx terser $(JS_SOURCES) \
		--compress \
		--mangle \
		--source-map "url=main.min.js.map" \
		--output $(JS_OUTPUT)
	@echo "Created: $(JS_OUTPUT)"

# Minify CSS
minify-css: $(CSS_OUTPUT)

$(CSS_OUTPUT): $(CSS_SOURCES)
	@echo "Minifying CSS..."
	npx cleancss -o $(CSS_OUTPUT) $(CSS_SOURCES)
	@echo "Created: $(CSS_OUTPUT)"

# Clean minified files
clean:
	@echo "Removing minified files..."
	rm -f $(JS_OUTPUT) $(CSS_OUTPUT)
	@echo "Clean complete."

# Watch for changes (requires inotify-tools on Linux)
watch:
	@echo "Watching for file changes..."
	@echo "Press Ctrl+C to stop"
	@while true; do \
		inotifywait -e modify,create $(JS_SRC_DIR)/*.js $(CSS_SRC_DIR)/*.css 2>/dev/null && \
		make minify; \
	done || echo "Note: install inotify-tools for file watching support"

# Run Django development server
run:
	@cd ram && python manage.py runserver

# Run Django tests
test:
	@echo "Running Django tests..."
	@cd ram && python manage.py test

# Run flake8 linter
lint:
	@echo "Running flake8..."
	@flake8 ram/

# Run black formatter
format:
	@echo "Running black formatter..."
	@black -l 79 --extend-exclude="/migrations/" ram/

# Run ruff linter
ruff-check:
	@echo "Running ruff check..."
	@ruff check ram/

# Run ruff formatter
ruff-format:
	@echo "Running ruff format..."
	@ruff format ram/

# Dump database to gzipped JSON file
# Usage: make dump-data FILE=backup.json.gz
dump-data:
ifndef FILE
	$(error FILE is not set. Usage: make dump-data FILE=backup.json.gz)
endif
	$(eval FILE_ABS := $(shell realpath -m $(FILE)))
	@echo "Dumping database to $(FILE_ABS)..."
	@cd ram && python manage.py dumpdata \
		--indent=2 \
		-e admin \
		-e contenttypes \
		-e sessions \
		--natural-foreign \
		--natural-primary | gzip > $(FILE_ABS)
	@echo "✓ Database dumped successfully to $(FILE_ABS)"

# Load data from fixture file
# Usage: make load-data FILE=backup.json.gz
load-data:
ifndef FILE
	$(error FILE is not set. Usage: make load-data FILE=backup.json.gz)
endif
	$(eval FILE_ABS := $(shell realpath $(FILE)))
	@echo "Loading data from $(FILE_ABS)..."
	@cd ram && python manage.py loaddata $(FILE_ABS)
	@echo "✓ Data loaded successfully from $(FILE_ABS)"
