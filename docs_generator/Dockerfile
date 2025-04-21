FROM python:3.11-slim

WORKDIR /src

# Install only pdoc
RUN pip install --no-cache-dir pdoc

# Copy source files
COPY alerts_service /src/alerts_service
COPY analytics_service /src/analytics_service
COPY collector_service /src/collector_service
COPY flask_api /src/flask_api
COPY sensor_script.py /src/

# Create __init__.py files
RUN touch /src/alerts_service/__init__.py \
    /src/analytics_service/__init__.py \
    /src/collector_service/__init__.py \
    /src/flask_api/__init__.py

# Create simple wrapper script
RUN echo '#!/bin/python3\n\
import os\n\
import pdoc\n\
import sys\n\
\n\
modules = [\n\
    "alerts_service",\n\
    "analytics_service",\n\
    "collector_service",\n\
    "flask_api",\n\
    "sensor_script"\n\
]\n\
\n\
pdoc.render.configure(docformat="google", show_source=False)\n\
\n\
for module in modules:\n\
    try:\n\
        doc = pdoc.pdoc(module)\n\
        output_file = os.path.join("/output", f"{module}.html")\n\
        with open(output_file, "w", encoding="utf-8") as f:\n\
            f.write(doc)\n\
    except Exception as e:\n\
        print(f"Warning: Could not generate docs for {module}: {e}", file=sys.stderr)\n\
        continue' > /src/run_pdoc.py && \
    chmod +x /src/run_pdoc.py

ENV PYTHONPATH=/src

CMD ["python", "/src/run_pdoc.py"]