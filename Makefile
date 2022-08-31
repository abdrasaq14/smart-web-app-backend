DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint:
	./scripts/lint.sh

.PHONY: clean
clean: clean_pyc

.PHONY: clean_pyc
clean_pyc: ## Clean all *.pyc in the system
	find . -type f -name "*.pyc" -delete || true

.PHONY: migrate
migrate: # Runs the migrations
	python src/manage.py migrate --noinput

.PHONY: migrations
migrations: ## Generate migrations
	python src/manage.py makemigrations

.PHONY: requirements
requirements: ## Install the requirements
	pip install -r requirements/development.txt

.PHONY: run
run: ### Starts the development server
	python src/manage.py runserver

.PHONY: run_plus
run_plus: ## Starts the development server with django extensions runserver_plus
	python src/manage.py runserver_plus

.PHONY: shell
shell: ## Starts the shell using django extensions shell_plus
	python src/manage.py shell_plus

.PHONY: show_urls
show_urls: ## Shows the available urls
	python src/manage.py show_urls

.PHONY: test
test: ## Runs the tests
	cd src && \
	pytest $(TESTONLY) --disable-pytest-warnings -s -vv $(CREATE_DB) && \
	cd .

.PHONY: go
go: ## Starts the venv, sources the files and starts the server
	source venv/bin/activate

ifndef VERBOSE
.SILENT:
endif
