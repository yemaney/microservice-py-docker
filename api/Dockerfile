FROM python:3.12-slim

WORKDIR /src/api

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

WORKDIR /src

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=5s --timeout=5s --retries=5 CMD curl --include --request GET http://localhost:8000/healthcheck || exit 1
