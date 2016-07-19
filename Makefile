run:
	python -m timebook.timebook

test:
	py.test tests

watch:
	watch -n 1 cat timesheet.json
