.PHONY: requirements badge compose checks

# Target to update requirements.txt
requirements:
	@FAILED=false; \
	NEW_REQUIREMENTS=$$(poetry export -f requirements.txt --without-hashes --with dev); \
	if [ -f requirements.txt ]; then \
		echo "requirements.txt exists!"; \
	else \
		echo "FAILURE: requirements.txt does not exist!"; \
		poetry export --format requirements.txt --output requirements.txt --without-hashes --with dev; \
		FAILED=true; \
	fi; \
	REQUIREMENTS=$$(cat requirements.txt); \
	if [ "$$NEW_REQUIREMENTS" = "$$REQUIREMENTS" ]; then \
		echo "requirements.txt is up to date!"; \
	else \
		echo "FAILURE: requirements.txt is not up to date!"; \
		poetry export --format requirements.txt --output requirements.txt --without-hashes --with dev; \
		FAILED=true; \
	fi; \
	if [ "$$FAILED" = true ]; then \
		exit 1; \
	fi; \
	exit 0

# Target to create coverage badge
badge:
	@pytest -s --cov
	@echo "Creating coverage badge"
	@if [ -f ./docs/images/coverage.svg ]; then \
		echo "deleting old badge"; \
		rm ./docs/images/coverage.svg; \
	fi; \
	coverage-badge -o ./docs/images/coverage.svg
	@echo "Removing .coverage file"
	@rm .coverage
	@echo "done"

compose:
	@docker-compose down
	@if docker images | awk '$$1=="microservice-py-docker-api" && $$2=="latest" {found=1; exit} END {exit !found}'; then \
	    docker rmi microservice-py-docker-api:latest; \
	fi
	@if docker images | awk '$$1=="microservice-py-docker-backend" && $$2=="latest" {found=1; exit} END {exit !found}'; then \
	    docker rmi microservice-py-docker-backend:latest; \
	fi
	@docker-compose up -d

checks:
	make compose
	@sleep 10
	make badge
	make requirements
	@pre-commit
