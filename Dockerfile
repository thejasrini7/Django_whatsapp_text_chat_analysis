FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p static staticfiles media

# Collect static files
RUN python manage_render.py collectstatic --noinput

# Run migrations
RUN python manage_render.py migrate

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "myproject.wsgi_render:application", "--bind", "0.0.0.0:8000"]