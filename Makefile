MANAGE := poetry run python3 manage.py

dev:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

start:
	poetry run gunicorn queue_manager.wsgi

db-container:
	docker compose up -d