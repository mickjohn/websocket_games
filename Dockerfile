FROM alpine:3.10

COPY requirements.txt setup.py README.txt MANIFEST /
COPY websocketgames /websocketgames
COPY setup.py .
# RUN apk update && apk add python3 --no-cache && pip3 install -r requirements.txt
RUN apk update \
    && apk add python3 --no-cache \
    && apk add gcc --no-cache \
    && apk add python3-dev --no-cache \
    && apk add linux-headers --no-cache \
    && apk add musl-dev --no-cache \
    && pip3 install -r requirements.txt \
    && pip3 install -e .

EXPOSE 8080

CMD /usr/bin/python3 websocketgames/main.py
# CMD /bin/sh

