FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/tools/python_indicator_clone/src

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r tools/python_indicator_clone/requirements.txt \
 && pip install --no-cache-dir -r services/api/requirements.txt

EXPOSE 8080
CMD ["uvicorn", "services.api.data_api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
