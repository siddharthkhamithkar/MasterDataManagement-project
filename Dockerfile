# Use official Python base image (Linux-based)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Run FastAPI using Uvicorn with host set to 0.0.0.0 for external access
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
