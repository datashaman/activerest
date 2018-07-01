test:
	python setup.py test

clean:
	rm -rf activerest/__pycache__/
	find . -name '*.pyc' -delete
