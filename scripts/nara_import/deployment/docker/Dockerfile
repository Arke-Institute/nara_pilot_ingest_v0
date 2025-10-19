FROM python:3.11-slim

# Install AWS CLI for S3 access
RUN apt-get update && \
    apt-get install -y awscli curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire nara_import directory
COPY . .

# Default command - runs full import
# Override with import_limited.py or test_import_sample.py as needed
CMD ["python", "import_full_collection.py"]
