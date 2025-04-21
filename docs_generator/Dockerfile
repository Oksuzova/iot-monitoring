FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pdoc

COPY docs_generator/generate_docs.py /app/
RUN chmod +x /app/generate_docs.py

ENV PYTHONPATH=/src

CMD ["python", "/app/generate_docs.py"]