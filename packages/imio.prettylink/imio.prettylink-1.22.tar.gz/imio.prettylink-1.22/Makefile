#!/usr/bin/make
#
all: run

.PHONY: bootstrap buildout run test cleanall
bootstrap:
	if command -v python2 >/dev/null && command -v virtualenv; then virtualenv -p python2 . ; elif command -v virtualenv-2.7; then virtualenv-2.7 . ;fi
	bin/pip install -r requirements.txt

buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -Nt 5

run:
	if ! test -f bin/instance;then make buildout;fi
	bin/instance fg

test:
	if ! test -f bin/test;then make buildout;fi
	rm -fr htmlcov
	bin/coverage.sh

cleanall:
	rm -fr bin develop-eggs htmlcov include .installed.cfg lib .mr.developer.cfg parts downloads eggs
