FROM python:3.12-slim

# Copy backend requirements first
COPY backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tmp/backend-requirements.txt

# Copy the entire project
COPY . /src

WORKDIR /src

EXPOSE 8080
