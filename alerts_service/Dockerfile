# Base image: Python 3.9 slim version for a smaller footprint
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
# Using --no-cache-dir reduces the image size by not caching pip packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Command to run the application
CMD ["python", "app.py"]