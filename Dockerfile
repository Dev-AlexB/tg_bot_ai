FROM python:3.13.6-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
