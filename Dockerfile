FROM alpine:3.10

COPY requirements.txt setup.py README.txt MANIFEST /
COPY websocketgames /websocketgames
COPY setup.py .

RUN apk update \
    && apk add python3 python3-dev gcc linux-headers  musl-dev --no-cache \
    && pip3 install -r requirements.txt \
    && pip3 install -e .

EXPOSE 8080

CMD /usr/bin/python3 websocketgames/main.py