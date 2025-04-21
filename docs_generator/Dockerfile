FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install pdoc
RUN pip install --no-cache-dir pdoc

# Create directories for source and output
RUN mkdir -p /app/src /app/output

# Copy the script first
COPY docs_generator/generate_docs.py /app/

# Set permissions
RUN chmod +x /app/generate_docs.py

# Set Python path to include source directory
ENV PYTHONPATH=/app/src

# Run script
CMD ["python", "/app/generate_docs.py"]