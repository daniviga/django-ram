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
	npx terser $(JS_SOURCES) -c -m -o $(JS_OUTPUT)
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
