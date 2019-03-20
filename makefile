PYTHON=./env/bin/python3
SRC=./odk2stata


.PHONY: lint test dist test-upload upload clean

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC}
	${PYTHON} -m pycodestyle ${SRC}
	${PYTHON} -m pydocstyle ${SRC}

test:
	${PYTHON} -m unittest discover -v

dist: clean
	${PYTHON} setup.py sdist bdist_wheel

test-upload: dist
	${PYTHON} -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: dist
	${PYTHON} -m twine upload dist/*

clean:
	rm -rf dist/
	rm -rf *.egg-info/
