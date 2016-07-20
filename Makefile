DATADIR = data/
DATE = `date +%Y-%m-%d`

run:
	python -m timebook.timebook

test:
	py.test tests

watch:
	watch -n 1 cat $(DATADIR)$(DATE).json
