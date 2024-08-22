.PHONY: run
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery:
	celery -A app.celery_app worker --loglevel=info

env:
	virtualenv .env -p python3.10

dev:
	pip install -r requirements.txt
	pre-commit clean
	pre-commit install

pre-commit:
	pre-commit run --all-files