test:
	python setup.py -q test

coverage:
	coverage run --source activerest setup.py -q test
	coverage report -m

coveralls:
	coveralls

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

develop:
	python setup.py -q develop
