test:
	python setup.py -q test

coverage:
	coverage run --source activerest setup.py -q test
	coverage report -m

coveralls:
	coveralls

clean:
	rm -rf activerest/__pycache__/
	find . -name '*.pyc' -delete

develop:
	python setup.py -q develop
