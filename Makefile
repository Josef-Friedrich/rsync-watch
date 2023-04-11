build:
	rm -rf dist
	python3 setup.py sdist

upload:
	pip3 install twine
	twine upload --skip-existing dist/*

install:
	poetry install

update:
	poetry lock
	poetry install

test:
	pip3 install tox
	poetry run tox

doc:
	tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: build upload test doc
