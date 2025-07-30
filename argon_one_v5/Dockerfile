ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache \
    python3 \
    py3-pip \
    i2c-tools \
    py3-smbus \
    py3-pillow \
    ttf-dejavu \
    py3-psutil

# Create virtual environment and install luma packages
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
    luma.oled \
    luma.core

WORKDIR /
COPY run.py /

# Use the virtual environment's Python
CMD ["/opt/venv/bin/python3", "-u", "/run.py"]
