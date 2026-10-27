FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UNRAR_TOOL=unrar

WORKDIR /app

# Enable non-free repositories for unrar
RUN sed -i 's/Components: main/Components: main contrib non-free/' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/main$/main contrib non-free/' /etc/apt/sources.list 2>/dev/null

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    unrar \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "download_and_prepare_bearing_data.py"]
CMD ["--help"]
