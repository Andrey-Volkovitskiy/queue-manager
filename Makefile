MANAGE := poetry run python3 manage.py

dev:
	$(MANAGE) runserver

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

start:
	poetry run gunicorn queue_manager.wsgi

colletstatic:
	$(MANAGE) collectstatic --noinput

railway-start:
	python manage.py migrate && python collectstatic --noinput && gunicorn queue_manager.wsgi

db-container:
	docker compose up -d

install:
	poetry install

test:
	poetry run python3 -m pytest -ra -s -vvv tests/

cov:
	poetry run python3 -m pytest --cov=queue_manager/

lint:
	poetry run flake8 queue_manager

shell:
	$(MANAGE) shell