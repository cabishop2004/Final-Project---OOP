PYTHON = python
PYTEST = pytest

SOURCE_DIRS = \
	models \
	adapters \
	providers \
	services \
	storage \
	notifiers

.PHONY: install
install:
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: run
run:
	$(PYTHON) app.py

.PHONY: syntax
syntax:
	$(PYTHON) -m compileall \
		app.py \
		$(SOURCE_DIRS)

.PHONY: test
test:
	$(PYTEST) -v tests

.PHONY: coverage
coverage:
	$(PYTEST) \
		--cov=models \
		--cov=adapters \
		--cov=providers \
		--cov=services \
		--cov=storage \
		--cov=notifiers \
		--cov-report=term-missing \
		tests

.PHONY: style
style:
	flake8 \
		app.py \
		models \
		adapters \
		providers \
		services \
		storage \
		notifiers \
		tests

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf \
		.pytest_cache \
		.mypy_cache \
		htmlcov
	rm -f .coverage

.PHONY: check
check: syntax test
	@echo "Project syntax and tests passed"
