# Use Python 3.10 slim base image for reduced container size
# while maintaining full Python functionality
FROM python:3.10-slim

# Set the working directory inside the container
# All subsequent commands will be executed from this directory
WORKDIR /app

# Copy the entire Flask API application source code
# including requirements.txt and application files
COPY . .

# Install Python dependencies from requirements.txt
# --no-cache-dir reduces the image size by not caching downloaded packages
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to start the Flask API service
# Uses Python interpreter to run app.py as the entry point
CMD ["python", "app.py"]