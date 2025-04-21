FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install pdoc and required packages
RUN pip install --no-cache-dir pdoc

# Create necessary directories
RUN mkdir -p /app/src /app/output /app/mocks

# Copy mocks and scripts
COPY docs_generator/mocks /app/mocks
COPY docs_generator/generate_docs.py /app/

# Set permissions
RUN chmod +x /app/generate_docs.py
RUN chmod -R 777 /app/output

# Set Python path to include source and mocks
ENV PYTHONPATH=/app/src:/app/mocks

# Run script
CMD ["python", "/app/generate_docs.py"]