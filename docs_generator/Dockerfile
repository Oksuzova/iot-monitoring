FROM python:3.11-slim

WORKDIR /src

RUN pip install --no-cache-dir pdoc

COPY . .

COPY docs_generator/generate_docs.py /src/
RUN chmod +x /src/generate_docs.py

ENV PYTHONPATH=/src

CMD ["python", "/src/generate_docs.py"]