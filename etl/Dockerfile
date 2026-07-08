from python:3.11-slim

workdir /workspace

copy etl/requirements.txt /tmp/requirements.txt
run pip install --no-cache-dir -r /tmp/requirements.txt

copy etl /workspace/etl
copy data /workspace/data

entrypoint ["python", "etl/load_market_data.py"]
