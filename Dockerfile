# FROM alpine:3.10
FROM python:3.8-alpine3.10

COPY requirements.txt setup.py README.txt MANIFEST /
COPY websocketgames /websocketgames
COPY setup.py .

    # && apk add python3 python3-dev gcc linux-headers  musl-dev --no-cache \
RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir -e .

EXPOSE 8080

CMD python websocketgames/main.py
