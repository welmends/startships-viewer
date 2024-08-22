FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN rm -rf __pycache__ .env
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]