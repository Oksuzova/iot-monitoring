FROM python:3.11-slim

WORKDIR /src

RUN pip install --no-cache-dir pdoc

COPY . .

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
        html = pdoc.pdoc(module)\n\
        output_file = os.path.join("/output", f"{module}.html")\n\
        with open(output_file, "w", encoding="utf-8") as f:\n\
            f.write(html)\n\
    except Exception as e:\n\
        print(f"Warning: Could not generate docs for {module}: {e}", file=sys.stderr)\n\
        continue\n\
\n\
# Generate index.html\n\
index = "<html><head><title>API Documentation</title></head><body>"\n\
index += "<h1>API Documentation</h1><ul>"\n\
for module in modules:\n\
    index += f\'<li><a href="{module}.html">{module}</a></li>\'\n\
index += "</ul></body></html>"\n\
\n\
with open("/output/index.html", "w") as f:\n\
    f.write(index)' > /src/run_pdoc.py && chmod +x /src/run_pdoc.py

ENV PYTHONPATH=/src

CMD ["python", "/src/run_pdoc.py"]