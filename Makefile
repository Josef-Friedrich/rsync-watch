build:
	rm -rf dist
	python3 setup.py sdist

upload:
	pip3 install twine
	twine upload --skip-existing dist/*

test:
	pip3 install tox
	tox

doc:
	tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: build upload test doc
