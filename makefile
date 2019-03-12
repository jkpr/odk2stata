PYTHON=./env/bin/python3
SRC=./odk2stata


.PHONY: lint test dist test-upload upload clean

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC}
	${PYTHON} -m pycodestyle ${SRC}
	${PYTHON} -m pydocstyle ${SRC}

test:
	${PYTHON} -m unittest discover -v

dist:
	${PYTHON} setup.py sdist bdist_wheel

test-upload:
	${PYTHON} -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	${PYTHON} -m twine upload dist/*

clean:
	rm -rf dist/
	rm -rf *.egg-info/
