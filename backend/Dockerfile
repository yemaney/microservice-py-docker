FROM python:3.9.5-slim

WORKDIR /src/backend

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

WORKDIR /src

EXPOSE 8080
