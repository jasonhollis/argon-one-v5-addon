ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache \
    python3 \
    i2c-tools \
    py3-smbus \
    py3-pillow \
    ttf-dejavu

# Create virtual environment and install ALL needed packages
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
    luma.oled \
    luma.core \
    pytz \
    requests

WORKDIR /
COPY run.py /

# Use the virtual environment's Python
CMD ["/opt/venv/bin/python3", "-u", "/run.py"]
