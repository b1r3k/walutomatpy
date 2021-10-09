# Some simple testing tasks (sorry, UNIX only).

PYTHON=venv/bin/python3
PIP=venv/bin/pip
NOSE=venv/bin/nosetests
FLAKE=venv/bin/flake8
FLAGS=--with-coverage --cover-inclusive --cover-erase --cover-package=src --cover-min-percentage=47


update:
	$(PYTHON) setup.py develop

env:
	test -d venv || python3 -m venv venv

remove-env:
	test -d venv && rm -rf venv

force-env: remove-env env

install: env
	$(PYTHON) setup.py develop

reinstall: force-env install

flake:
	$(FLAKE) src tests

test: flake
	$(NOSE) -s $(FLAGS)

testloop:
	watch -n 3 $(NOSE) -x -s $(FLAGS)

cov cover coverage:
	$(NOSE) -s --with-cover --cover-html --cover-html-dir ./coverage $(FLAGS)
	echo "open file://`pwd`/coverage/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build

