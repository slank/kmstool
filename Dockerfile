FROM gliderlabs/alpine:latest

ADD . /code
RUN apk-install \
        python \
        python-dev \
        py-pip \
        gcc \
        libc-dev \
        libgcc \
    && pip install /code \
    && apk del \
        gcc \
        libc-dev \
        libgcc
