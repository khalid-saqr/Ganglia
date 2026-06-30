FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8717
CMD ["ganglia", "serve", "--host", "0.0.0.0", "--port", "8717"]
