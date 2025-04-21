import os
import pdoc
import sys

modules = [
    "alerts_service",
    "analytics_service",
    "collector_service",
    "flask_api",
    "sensor_script"
]

pdoc.render.configure(docformat="google", show_source=False)

for module in modules:
    try:
        html = pdoc.pdoc(module)
        output_file = os.path.join("/output", f"{module}.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"Warning: Could not generate docs for {module}: {e}", file=sys.stderr)
        continue

index = "<html><head><title>API Documentation</title></head><body>"
index += "<h1>API Documentation</h1><ul>"
for module in modules:
    index += f'<li><a href="{module}.html">{module}</a></li>'
index += "</ul></body></html>"

with open("/output/index.html", "w") as f:
    f.write(index)