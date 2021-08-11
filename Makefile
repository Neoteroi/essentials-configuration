.PHONY: release test


artifacts: test
	python setup.py sdist bdist_wheel


clean:
	rm -rf dist/


prepforbuild:
	pip install --upgrade twine setuptools wheel


testrelease:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*


release: clean artifacts
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*


test:
	pytest


testcov:
	pytest --cov-report html --cov=configuration tests/


lint: check-flake8 check-isort check-black


check-flake8:
	@echo "$(BOLD)Checking flake8$(RESET)"
	@flake8 . 2>&1


check-isort:
	@echo "$(BOLD)Checking isort$(RESET)"
	@isort --check-only . 2>&1


check-black:
	@echo "$(BOLD)Checking black$(RESET)"
	@black --check . 2>&1


format:
	@echo "$(BOLD)Formatting code 🧹 🧼$(RESET)"
	@black . 2>&1
	@isort . 2>&1
