.PHONY: requirements badge compose checks init act-build-docs act-test

# Target to initialize development environment
init:
	@sudo apt update
	@sudo apt install bash-completion -y
	@pipx install uv
	@sudo curl https://raw.githubusercontent.com/yemaney/gitmoji-sh/main/gitmoji.sh -o /usr/bin/gitmoji
	@sudo chmod +x /usr/bin/gitmoji
	@curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash -s -- -b /usr/local/bin

# Target to update requirements.txt files
requirements:
	@uv sync
	@FAILED=false; \
	NEW_REQUIREMENTS=$$(uv export --format requirements-txt); \
	# Check and update main requirements.txt \
	if [ -f requirements.txt ]; then \
		echo "requirements.txt exists!"; \
	else \
		echo "FAILURE: requirements.txt does not exist!"; \
		uv export --format requirements-txt > requirements.txt; \
		FAILED=true; \
	fi; \
	REQUIREMENTS=$$(cat requirements.txt); \
	if [ "$$NEW_REQUIREMENTS" = "$$REQUIREMENTS" ]; then \
		echo "requirements.txt is up to date!"; \
	else \
		echo "FAILURE: requirements.txt is not up to date!"; \
		uv export --format requirements-txt > requirements.txt; \
		FAILED=true; \
	fi; \
	# Update api/requirements.txt \
	uv export --format requirements-txt > api/requirements.txt; \
	echo "api/requirements.txt updated!"; \
	# Update backend/requirements.txt \
	uv export --format requirements-txt > backend/requirements.txt; \
	echo "backend/requirements.txt updated!"; \
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
	@trap 'docker-compose down' EXIT; \
	pytest -s --cov && \
	make requirements && \
	pre-commit

# Target to run build-docs GitHub Action locally with act
act-build-docs:
	@act -j deploy -W .github/workflows/build-docs.yaml

# Target to run test GitHub Action locally with act
act-test:
	@act -j build -W .github/workflows/test.yaml
