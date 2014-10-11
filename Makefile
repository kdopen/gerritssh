.PHONY: help clean clean-pyc clean-build list test test-all coverage docs release sdist

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean - Includes clean-build and clean-pyc"
	@echo "clean-dist - Includes 'make clean' but also wipes the .tox directory and all eggs"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-online - Same as 'make test' but includes online checks"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-all-online - Same as 'make test-all' but includes online checks"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr docs/build/
	rm -fr docs/_build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr htmlcov/
	rm -fr .coverage
	make -C docs clean

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-sdist: clean
	rm -rf .tox/
	find . -name '*.egg' -exec rm -f {} +

lint:
	flake8 gerritssh test

test:
	py.test -l

test-online:
	GSSH_TEST_INSTANCE='review.openstack.org' py.test -l


test-all:
	tox

test-all-online:
	GSSH_TEST_INSTANCE='review.openstack.org' tox

coverage:
	coverage run --source gerritssh --branch setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/gerritssh.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ gerritssh
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist
