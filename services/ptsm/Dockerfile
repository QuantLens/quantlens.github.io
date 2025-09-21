FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/tools/python_indicator_clone/src

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r tools/python_indicator_clone/requirements.txt \
 && pip install --no-cache-dir -r services/ptsm/requirements.txt

EXPOSE 8081
CMD ["uvicorn", "services.ptsm.app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "2"]
