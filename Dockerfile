# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN pip install uv

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Initialize uv and add dependencies from requirements.txt
RUN uv init
RUN uv add -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8091

# Run the application with the specified host and port
CMD ["uv", "run", "main.py", "--host", "0.0.0.0", "--port", "8091"]
