FROM python:3.9.5

WORKDIR /src/api

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

WORKDIR /src

EXPOSE 8000
