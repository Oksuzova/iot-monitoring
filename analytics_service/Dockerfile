# Use Python 3.9 slim base image to minimize container size
# while providing all necessary Python runtime dependencies
FROM python:3.9-slim

# Set the working directory for the application
WORKDIR /app

# Copy requirements file first to leverage Docker cache
# This layer will only rebuild if requirements.txt changes
COPY requirements.txt /app/

# Install Python dependencies
# --no-cache-dir reduces the image size by not caching pip download files
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# This should be after dependencies to optimize rebuilds
COPY . /app

# Command to run the analytics service
# Uses the default Python interpreter with app.py as the entry point
CMD ["python", "app.py"]