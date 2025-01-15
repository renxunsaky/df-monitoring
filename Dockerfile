# Use Python slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory and set permissions
RUN mkdir -p logs && \
    chown -R 1000:1000 /app/logs && \
    chmod 755 /app/logs

# Verify installed packages
RUN pip list

# Expose port
EXPOSE 5000

# Set the user
USER 1000

# Run the application with Gunicorn
CMD ["python", "app.py"]