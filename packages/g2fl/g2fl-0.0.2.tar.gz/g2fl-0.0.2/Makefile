pkg:
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade build
	python3 -m build

push:
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*


gen-requirements:
	python3 -m pip install --upgrade pipreqs
	pipreqs .

.PHONY:
	clean

clean:
	rm -rf dist requirements.txt