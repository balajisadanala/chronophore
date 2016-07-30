DATADIR = data/
DATE = `date +%Y-%m-%d`

init:
	pip install -r requirements.txt

test:
	# To run individual tests, use "py.test -k the_test_path"
	py.test tests

lint:
	pycodestyle timebook/*.py tests/*.py

run:
	python -m timebook

watch:
	watch -n 1 cat $(DATADIR)$(DATE).json

loc:
	cloc --by-file --include-lang=Python timebook/ tests/

coverage:
	py.test --verbose --cov-report term --cov=timebook tests

todo:
	grep -FR --ignore-case --binary-file=without-match todo timebook/ tests/
