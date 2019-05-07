export REPOSITORY=amundsensearchlibrary
include boilerplate/lyft/docker_build/Makefile

.PHONY: test
clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit
test_unit:
	python3 -bb -m pytest tests

.PHONY: install
install:
	pip3 install -r requirements.txt && pip3 install mypy


.PHONY: lint
lint:
	flake8 .

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports --follow-imports=skip --strict-optional --warn-no-return search_service

.PHONY: test
test: test_unit lint mypy
