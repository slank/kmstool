FROM gliderlabs/alpine:latest

ADD . /code
RUN apk-install \
        python \
        py-pip \
        python-dev \
        gcc \
        libc-dev \
        libgcc \
    && pip install /code \
    && apk del \
        python-dev \
        gcc \
        libc-dev \
        libgcc
