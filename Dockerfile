FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create directories for documents and data persistence
RUN mkdir -p documents data

# Set environment variable for database connection
ENV DATABASE_URL=postgresql+psycopg://postgres:password@postgres:5432/vectordb

# Default to keeping container alive - run the app manually
# CMD ["tail", "-f", "/dev/null"]

# Run the main script
CMD ["python", "rag-app.py"]
