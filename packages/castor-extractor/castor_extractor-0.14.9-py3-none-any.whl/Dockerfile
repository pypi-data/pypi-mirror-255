# syntax=docker/dockerfile:1.5

FROM --platform=linux/amd64 python:3.10-slim

ARG EXTRA
ENV EXTRA=${EXTRA}

RUN pip install --upgrade pip && \
    pip install castor-extractor[${EXTRA}]

ENV CASTOR_OUTPUT_DIRECTORY=/data

VOLUME [ "/data" ]

ENTRYPOINT castor-extract-${EXTRA}
CMD [ "--log-to-stdout" ]
