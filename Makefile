.PHONY: cheers
cheers:
	@echo "Na zdraví! 🍺🍺🍺🍺🍺"

.PHONY: dev
dev:
	@docker compose -f docker-compose.yml up --build

.PHONY: run
run:
	@docker compose -f docker-compose.yml up --build -d

.PHONY: stop
stop:
	@docker compose -f docker-compose.yml down

.PHONY: down
down:
	@docker compose -f ./docker-compose.yml down --remove-orphans

.PHONY: tests
tests: run
	@echo "IMPLEMENT IT"
