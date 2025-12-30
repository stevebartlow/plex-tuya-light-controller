FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for Pillow)
# build-essential and libjpeg-dev are often needed for graphical libs
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the Flask port
EXPOSE 5001

# Run the application
CMD ["python", "-u", "server.py"]
