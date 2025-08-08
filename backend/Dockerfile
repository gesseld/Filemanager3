FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-por \
    openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Tika server
RUN mkdir -p /opt/tika && \
    wget https://archive.apache.org/dist/tika/tika-server-2.9.0.jar -O /opt/tika/tika-server.jar

COPY . .

# Start Tika server in background and main app
CMD ["sh", "-c", "java -jar /opt/tika/tika-server.jar & uvicorn main:app --host 0.0.0.0 --port 8000"]
