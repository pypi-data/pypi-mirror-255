#!/usr/bin/make
# pyenv is a requirement, with 2.7, 3.7 and 3.10 python versions, and virtualenv installed in each version
# plone parameter must be passed to create environment 'make setup plone=6.0' or after a make cleanall
# The original Makefile can be found on https://github.com/IMIO/scripts-buildout

SHELL=/bin/bash
pythons=2.7 3.10

ifeq (, $(shell which pyenv))
  $(error "pyenv command not found! Aborting")
endif

all: setup

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.python-version:  ## Setups pyenv version
	@pyenv local `pyenv versions |grep "  $(python)" |tail -1 |xargs`
	@echo "Local pyenv version is `cat .python-version`"
	@ if [[ `pyenv which virtualenv` != `pyenv prefix`* ]] ; then echo "You need to install virtualenv in `cat .python-version` pyenv python (pip install virtualenv)"; exit 1; fi

# Avoid this bug https://gitlab.kitware.com/cmake/cmake/-/issues/23425
# bin/python: .python-version  ## Setups environment
bin/pip: .python-version  ## Setups environment
	virtualenv .
	./bin/pip install --upgrade pip
	./bin/pip install pdbpp
	./bin/pip install -e .

.PHONY: setup
setup: oneof-python cleanall bin/pip  ## Setups environment

.PHONY: test
test: bin/pip  ## run tests
	bin/python -m unittest discover

.PHONY: cleanall
cleanall:  ## Cleans all installed buildout files
	rm -fr bin include lib .python-version pyvenv.cfg

.PHONY: which-python
which-python:  ## Displays versions information
	@echo "current python = `cat .python-version`"
	@echo "python var = $(python)"

.PHONY: guard-%
guard-%:
	@ if [ "${${*}}" = "" ]; then echo "You must give a value for variable '$*' : like $*=xxx"; exit 1; fi

.PHONY: oneof-%
oneof-%:
	@ if ! echo "${${*}s}" | tr " " '\n' |grep -Fqx "${${*}}"; then echo "Invalid '$*' parameter ('${${*}}') : must be one of '${${*}s}'"; exit 1; fi
