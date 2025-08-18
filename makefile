fmt:
	docker compose run --rm api black /app

lint:
	docker compose run --rm api black --check /app
