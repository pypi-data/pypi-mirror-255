.PHONY: clean-pyc test upload-docs docs

all: clean-pyc test

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

upload-docs:
	$(MAKE) -C docs html dirhtml epub
	cd docs/_build/; mv html nereid-docs; zip -r nereid-docs.zip nereid-docs; mv nereid-docs html
	scp -r docs/_build/dirhtml/* root@web:/srv/www/sites/nereid.m9s.biz/public
	scp docs/_build/nereid-docs.zip root@web:/srv/www/sites/nereid.m9s.biz/public/docs/nereid-docs.zip
	scp docs/_build/epub/Nereid.epub root@web:/srv/www/sites/nereid.m9s.biz/public/docs/nereid-docs.epub

docs:
	$(MAKE) -C docs html
