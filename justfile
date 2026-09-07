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

# Regenerate the metrics projection from the checked-in catalog sources (offline)
metrics-data:
    uv run --locked python -m build.metrics_catalog

# Generate vocabulary data and prepare every static site download from YAML sources
build:
    uv run --locked python -m build.build --site-public-dir {{site_dir}}/public

# Validate the canonical LinkML metamodel and composite
validate:
    uv run --locked python -m build.validate

# Validate external/<system>/matching.yaml files against build/schemas/matching.schema.json
validate-matchings:
    uv run --locked python -m build.validate_matchings

# Validate schema/value_crosswalks/*.yaml: schema conformance, TODO-free
# standards, and known source ids. Fails the build until every authored
# crosswalk has fully-populated standard metadata.
validate-crosswalks:
    uv run --locked python -m build.validate_crosswalks

# Legacy bespoke sources only: sync external standard vocabularies (refuses LinkML)
sync-standards:
    uv run --locked python -m build.sync_standards

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
    uv run --locked pytest

# Lint schema content for quality and style issues
lint:
    uv run --locked python -m build.lint

# Check translation completeness and staleness
check-translations:
    uv run --locked python -m build.check_translations

# Validate, lint, test, build, and check everything is clean
check: validate validate-crosswalks lint check-translations test build
    @echo "All checks passed."

# Install all dependencies (Python + Node)
setup:
    uv sync --locked
    cd {{site_dir}} && npm install

# Full clean rebuild: install deps, validate, build data, build site
all: setup validate build site-build
