# =============================================================================
# SHK-CMS Dockerfile
# =============================================================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        wget \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Angular
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database\n\
echo "Waiting for database..."\n\
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do\n\
  sleep 1\n\
done\n\
echo "Database available!"\n\
\n\
# Run migrations\n\
python manage.py migrate\n\
\n\
# Create superuser if not exists\n\
python manage.py shell -c "\n\
from django.contrib.auth import get_user_model;\n\
User = get_user_model();\n\
if not User.objects.filter(username='\''admin'\'').exists():\n\
    User.objects.create_superuser('\''admin'\'', '\''admin@shk-cms.local'\'', '\''admin123'\'')\n\
"\n\
\n\
# Start server\n\
exec "$@"' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]