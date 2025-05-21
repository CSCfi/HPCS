# Using Python original Docker image
ARG  BUILDPLATFORM=linux/amd64
FROM --platform=$BUILDPLATFORM python:3.9-alpine

# Install necessary packages and spire-agent
RUN apk add --no-cache \
    git=2.47.2-r0 \
    curl=8.12.1-r1 \
    build-base=0.5-r3 \
    openssl=3.3.3-r0
# Install spire-agent
RUN curl -LsSf -o spire-1.9.0-linux-amd64-musl.tar.gz https://github.com/spiffe/spire/releases/download/v1.9.0/spire-1.9.0-linux-amd64-musl.tar.gz && \
    tar xvf spire-1.9.0-linux-amd64-musl.tar.gz && \
    mv spire-1.9.0 /opt && \
    mv /opt/spire-1.9.0 /opt/spire && \
    ln -s /opt/spire/bin/spire-agent /usr/bin/spire-agent && \
    ln -s /opt/spire/bin/spire-server /usr/bin/spire-server && \
    rm -rf spire-1.9.0-linux-amd64-musl.tar.gz

# Copy server
COPY ./server /server

# Set workdir
WORKDIR /server

# Install dependencies
RUN pip install --no-cache-dir -r ./requirements.txt && \
    pip install --no-cache-dir git+https://github.com/HewlettPackard/py-spiffe.git@3640af9d6629c05e027f99010abc934cb74122a8

# Copy utils
COPY ./utils /server/utils

# Set entrypoint
ENTRYPOINT [ "./entrypoint.sh" ]
