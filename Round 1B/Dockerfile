FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY main.py .

RUN mkdir -p /app/input /app/output

ENV PERSONA="General Researcher"
ENV JOB="Extract relevant information from documents"

CMD ["python", "main.py"]
