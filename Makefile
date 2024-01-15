# Variables
VENV=.venv
PYTHON=$(VENV)/bin/python3
BIN=$(VENV)/bin/
SECRETS_SAMPLE=test/test_home/secrets-sample.yaml
SECRETS=test/test_home/secrets.yaml

all: $(BIN)activate

$(BIN)activate: requirements.txt setup.py setup.cfg
	python3 -m venv $(VENV)
	$(BIN)pip install -U pip setuptools wheel
	$(BIN)pip install -r requirements.txt

# a secrets.yaml is needed to run the test
$(SECRETS):
	cp -n $(SECRETS_SAMPLE) $(SECRETS)

$(BIN)pytest: $(BIN)activate requirements_test.txt
	$(BIN)pip install -r requirements_test.txt

# shortcuts to use as "Make venv" or "Make vent_test"
venv: $(BIN)activate
venv_test: $(BIN)pytest

.PHONY: test
test: venv_test $(SECRETS)
	$(BIN)pytest

.PHONY: release
release: clean test
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: upload
upload: release
	$(PYTHON) setup.py upload

# code linters
.PHONY: lint
lint: venv_test
	$(BIN)pre-commit run --all-files

.PHONY: lint-changed
lint-changed:
	git status --porcelain | egrep -v '^(D |RM|R )' | cut -b 4- | xargs pre-commit run --files

.PHONY: clean
clean:
	rm -fR $(VENV) .pytest_cache .mypy_cache __pycache__ elena.egg-info
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
