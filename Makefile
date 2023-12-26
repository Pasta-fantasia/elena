# Variables
VENV=.venv
PYTHON=$(VENV)/bin/python3
BIN=$(VENV)/bin/

$(VENV): requirements.txt requirements_test.txt setup.py
	python3 -m venv $(VENV)
	$(BIN)pip install -U pip setuptools wheel
	$(BIN)pip install -r requirements.txt
	$(BIN)pip install -r requirements_test.txt

.PHONY: test
test: $(VENV)
	$(PYTHON) -m pytest

.PHONY: release
release: clean test
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: upload
upload: release
    $(PYTHON) "setup.py upload -r http://TODO.com/pypi"

# code linters
.PHONY: lint
lint: $(VENV)
	$(BIN)pre-commit run --all-files

.PHONY: lint-changed
lint-changed:
	git status --porcelain | egrep -v '^(D |RM|R )' | cut -b 4- | xargs pre-commit run --files

.PHONY: clean
clean:
	rm -fR $(VENV) .pytest_cache .mypy_cache __pycache__ elena.egg-info
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
