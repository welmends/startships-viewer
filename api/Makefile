.PHONY: run
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery:
	celery -A app.celery_app worker --loglevel=info