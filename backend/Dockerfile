FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        libportaudio2 \
        libfluidsynth-dev \
        libportaudiocpp0 &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir -p /app/data

COPY ./src .

EXPOSE 8000

CMD ["uvicorn", "ai:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
