# PublicSchema build system
# Run `just` to see available recipes, `just dev` to start working.

set dotenv-load := false

schema_dir := "schema"
dist_dir := "dist"
site_dir := "site"

# List available recipes
default:
    @just --list

# --- Build ---

# Generate vocabulary.json, context.jsonld, JSON Schemas, and downloadable files from YAML sources
build:
    uv run python -m build.build
    rsync -a --include='*.csv' --include='*.xlsx' --include='*/' --exclude='*' {{dist_dir}}/downloads/ {{site_dir}}/public/
    rsync -a --delete {{dist_dir}}/schemas/ {{site_dir}}/public/schemas/
    cp {{dist_dir}}/vocabulary.json {{site_dir}}/public/vocabulary.json

# Validate all YAML source files (schema, referential integrity, translations)
validate:
    uv run python -m build.validate

# Sync external standard vocabularies (countries, currencies, languages, etc.)
sync-standards:
    uv run python -m build.sync_standards

# --- Site ---

# Start the dev server (rebuilds generated data first)
dev: build
    cd {{site_dir}} && npm run dev

# Production build of the site (validates and rebuilds data first)
site-build: validate build
    cd {{site_dir}} && npm run build

# Preview the production build locally
site-preview:
    cd {{site_dir}} && npm run preview

# Install site dependencies
site-install:
    cd {{site_dir}} && npm install

# --- Development ---

# Run all tests
test:
    uv run pytest

# Lint schema content for quality and style issues
lint:
    uv run python -m build.lint

# Check translation completeness and staleness
check-translations:
    uv run python -m build.check_translations

# Validate, lint, test, build, and check everything is clean
check: validate lint check-translations test build
    @echo "All checks passed."

# Install all dependencies (Python + Node)
setup:
    uv sync
    cd {{site_dir}} && npm install

# Full clean rebuild: install deps, validate, build data, build site
all: setup validate build site-build
