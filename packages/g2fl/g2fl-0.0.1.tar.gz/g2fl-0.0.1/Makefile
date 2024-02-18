pkg:
	python3 setup.py sdist bdist_wheel

push:
	/Users/gavinlhchen/miniconda3/envs/py38/twine upload dist/*

.PHONY:
	clean

clean:
	rm -rf build dist g2fl.egg-info