DATADIR = ~/.local/share/chronophore/
DATE = `date +%Y-%m-%d`

init:
	pip install -r requirements.txt

test:
	# To run individual tests, use "py.test -k the_test_path"
	py.test tests

lint:
	flake8 --max-line-length=90 chronophore/*.py tests/*.py scripts/*.py

package: test lint
	python setup.py sdist bdist_wheel

upload-test: package
	twine upload -r test dist/*

install-test:
	pip3 install --no-cache-dir -i https://testpypi.python.org/pypi chronophore --extra-index-url https://pypi.python.org/pypi

upload: package
	twine upload dist/*

run:
	python -m chronophore

watch-data:
	tail -f $(DATADIR)$(DATE).json

watch-log:
	tail -f debug.log

loc:
	cloc --by-file --include-lang=Python chronophore/ tests/

coverage:
	py.test --verbose --cov-report term --cov=chronophore tests

todo:
	grep -FR --ignore-case --binary-file=without-match todo *.py chronophore/ tests/
