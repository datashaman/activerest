test:
	python setup.py -q test

clean:
	rm -rf activerest/__pycache__/
	find . -name '*.pyc' -delete
