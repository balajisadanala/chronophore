DATADIR = data/
DATE = `date +%Y-%m-%d`

init:
	pip install -r requirements.txt

test:
	# To run individual tests, use "py.test -k the_test_path"
	py.test tests

lint:
	flake8 timebook/*.py tests/*.py scripts/*.py

run:
	python -m timebook

watch-data:
	tail -f $(DATADIR)$(DATE).json

watch-log:
	tail -f debug.log

loc:
	cloc --by-file --include-lang=Python timebook/ tests/

coverage:
	py.test --verbose --cov-report term --cov=timebook tests

todo:
	grep -FR --ignore-case --binary-file=without-match todo timebook/ tests/
