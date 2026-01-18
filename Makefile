.PHONY: $(MAKECMDGOALS)

RED=\033[31m
GREEN=\033[32m
YELLOW=\033[33m
CYAN=\033[36m
RESET=\033[0m

up: ## Up bot container
	@echo "$(YELLOW)Start bot container...$(RESET)"
	@docker compose up -d --build
	@echo "$(GREEN)Bot container is started$(RESET)"

down: ## Down bot container
	@echo "$(YELLOW)Stop bot container...$(RESET)"
	@docker compose down
	@echo "$(GREEN)Bot container is stopped$(RESET)"

clear: ## Clear volumes
	@echo "$(YELLOW)Clear bot volumes...$(RESET)"
	@docker compose down -v
	@echo "$(GREEN)Bot volumes is cleaned$(RESET)"

logs: ## Check logs
	@echo "$(YELLOW)Open bot logs...$(RESET)"
	@docker compose logs -f
	@echo "$(GREEN)Bot logs is closed$(RESET)"


soft-reset: ## Reset container without deleting volumes
	@$(MAKE) down
	@$(MAKE) up

hard-reset: ## Reset container with deleting volumes
	@$(MAKE) clear
	@$(MAKE) up

## Optional
check-logs: ## Claude check errors in logs
	@docker compose logs | claude

.DEFAULT_GOAL := help

help: ## Shows a list of available commands
	@echo "$(GREEN)=====================================================================$(RESET)"
	@echo "$(GREEN)>>> Telegram Bot Commands:$(RESET)"
	@echo "$(GREEN)=====================================================================$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo "$(GREEN)=====================================================================$(RESET)"
