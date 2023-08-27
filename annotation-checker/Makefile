build:
	python -m build
	python -m twine upload dist/*

build test:
	python -m build
	twine upload --repository testpypi dist/*
	python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --upgrade acheck