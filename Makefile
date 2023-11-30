install:
	pip install -r requirements.txt
	pip install -r requirements_test.txt

setup: install
	pre-commit install

# code linters
lint:
	pre-commit run --all-files

lint-changed:
	git status --porcelain | egrep -v '^(D |RM|R )' | cut -b 4- | xargs pre-commit run --files
