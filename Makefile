testenv:
	pip install -e .
	pip install -r test_requirements.txt
	pip install Django

flake8:
	flake8 django_compressor_mako

runtests:
	coverage run --branch --source=django_compressor_mako \
		`which django-admin.py` \
		test --settings=compressor.test_settings \
		django_compressor_mako/tests

coveragereport:
	coverage report --omit=django_compressor_mako/test*

test: flake8 runtests coveragereport

.PHONY: test runtests flake8 coveragereport
