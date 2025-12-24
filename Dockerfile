# Use official Python runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Koyeb usually sets $PORT)
ENV PORT=8000

# Run the application
# We use the shell form to allow variable environment expansion if needed, 
# but EXEC form is preferred. We'll stick to a simple CMD that works.
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} main:app"]
