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
	cp -a src\docs\_build\html\. ../../fgratzkowski.github.io
	cd ../../fgratzkowski.github.io
	git add --all
	git commit -am "update"
	git push

