FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN pip install git+https://github.com/DARDataServices/PythonCore.git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./collector.py"]