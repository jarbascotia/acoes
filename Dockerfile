FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

RUN mkdir -p /app/db

EXPOSE 3003

CMD ["python", "app.py"]
