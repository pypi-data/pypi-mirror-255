build:
	python -m build

.PHONY: check
check:
	twine check dist/*

.PHONY: upload-pypi
upload-pypi:
	twine upload dist/*

.PHONY: upload-testpypi
upload-testpypi:
	twine upload -r testpypi dist/*

.PHONY: gitignore
gitignore:  ## create a .gitignore file from templates
	bash config/make-gitignore.sh

.PHONY: pre-commit-init
pre-commit-init-default:  ## initialize pre-commit
	python3 -m pip install --upgrade pre-commit
	pre-commit install --install-hooks --overwrite

.PHONY: pre-commit-clean
pre-commit-clean-default:  ## clean pre-commit
	pre-commit clean

.PHONY: pre-commit-update
pre-commit-update-default: pre-commit-clean-default pre-commit-init-default  ## update pre-commit and hooks

.PHONY: update-config
update-config-default:  ## update config subtree
	git subtree pull --prefix config git@github.com:base-angewandte/config.git main --squash

.PHONY: help
help:  ## show this help message
	@echo 'usage: make [command] ...'
	@echo
	@echo 'commands:'
	@egrep -h '^(.+)\:.+##\ (.+)' ${MAKEFILE_LIST} | sed 's/-default//g' | sed 's/:.*##/#/g' | sort -t# -u -k1,1 | column -t -c 2 -s '#'
