build:
	python -m build
	python -m twine upload dist/*

buildtest:
	python -m build
	twine upload --repository testpypi dist/*
	python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --upgrade acheck
docs:
	rm -rf src\docs\_build
	src\docs\make.bat html
	rm -rf ../../fgratzkowski.github.io/docs/
	mkdir ../../fgratzkowski.github.io/docs/
	cp -a src\docs\_build\html\. ../../fgratzkowski.github.io/docs

