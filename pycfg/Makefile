all:

test:
	nosetests -c .noserc

vtest:
	nosetests -c .noserc -v 2>&1 | less

clean:
	find . -name '*.pyc' | xargs -r rm -v
	find . -name '*~' | xargs -r rm -v
	find . -name '.*.sw?' | xargs -r rm -v
