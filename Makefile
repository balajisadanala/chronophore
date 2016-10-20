CONFIGDIR = ~/.config/chronophore/
DATADIR = ~/.local/share/chronophore/
LOGDIR = ~/.cache/chronophore/log/
DATE = `date +%Y-%m-%d`
SEPARATOR = "==================================================================================="

clean:
	rm -rf .tox/
	rm -rf build/
	rm -rf dist/
	rm -rf chronophore.egg-info/

clean-home:
	rm -rf $(CONFIGDIR)
	rm -rf $(DATADIR)
	rm -rf $(LOGDIR)

init:
	pip install -r requirements.txt

test:
	# To run individual tests, use "py.test -k the_test_path"
	py.test tests

lint:
	flake8 --max-line-length=90 chronophore/*.py tests/*.py scripts/*.py setup.py

tox: clean
	tox

package: tox lint
	python setup.py sdist bdist_wheel

upload-test: package
	twine upload -r test dist/*

install-test:
	pip3 install --no-cache-dir -i https://testpypi.python.org/pypi chronophore --extra-index-url https://pypi.python.org/pypi

upload: package
	twine upload dist/*

run:
	python -m chronophore --testdb

log:
	tail -f $(LOGDIR)debug.log

loc:
	cloc --by-file --include-lang=Python chronophore/ tests/

coverage:
	py.test --verbose --cov-report term --cov=chronophore tests

todo:
	@echo $(SEPARATOR)
	@cat TODO.md
	@echo $(SEPARATOR)
	@grep -FR --ignore-case --binary-file=without-match todo *.py chronophore/ scripts/ tests/
	@echo $(SEPARATOR)
