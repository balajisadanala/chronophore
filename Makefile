DATADIR = data/
DATE = `date +%Y-%m-%d`

run:
	python -m timebook.timebook

test:
	py.test tests

lint:
	pycodestyle timebook/*.py tests/*.py

watch:
	watch -n 1 cat $(DATADIR)$(DATE).json

loc:
	cloc --by-file --include-lang=Python timebook/ tests/
