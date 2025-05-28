FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        libportaudio2 \
        libfluidsynth-dev \
        libportaudiocpp0 &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y git timidity ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data

COPY ./src .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
