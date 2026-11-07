# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /app/requirements.txt

COPY . /app

EXPOSE 8080
CMD ["python3", "main.py", "--stdio"]
