PYTHON=./env/bin/python3
SRC=./odk2stata


.PHONY: lint test

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC}
	${PYTHON} -m pycodestyle ${SRC}
	${PYTHON} -m pydocstyle ${SRC}

test:
	${PYTHON} -m unittest discover -v
