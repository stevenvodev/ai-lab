FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY simulator.py .

# Create data directory and log file
RUN mkdir -p /app/data && touch /app/data/system_metrics.log && chmod 666 /app/data/system_metrics.log

# Expose nothing (this is a background process)
EXPOSE 8080

# Run the simulator
CMD ["python", "simulator.py"]
