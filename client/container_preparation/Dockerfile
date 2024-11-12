# Using Python original Docker image
ARG  BUILDPLATFORM=linux/amd64
FROM --platform=$BUILDPLATFORM python:3.9-alpine

# Create code directory, output directory
RUN mkdir /container_preparation /output

# Copy useful data from the project
COPY ./client/container_preparation /container_preparation

# Copy utils for SPIFFEID creation ...
COPY ./utils /container_preparation/utils

# Set workdir
WORKDIR /container_preparation

# Install necessary packages
RUN apk add --no-cache \
    git=2.45.2-r0 \
    curl=8.11.0-r2 \
    jq=1.7.1-r0 \
    build-base=0.5-r3 \
    libffi-dev=3.4.6-r0
# Install spire-agent
RUN curl -LsSf -o spire-1.9.0-linux-amd64-musl.tar.gz https://github.com/spiffe/spire/releases/download/v1.9.0/spire-1.9.0-linux-amd64-musl.tar.gz && \
    tar xvf spire-1.9.0-linux-amd64-musl.tar.gz && \
    mv spire-1.9.0 /opt && \
    mv /opt/spire-1.9.0 /opt/spire && \
    ln -s /opt/spire/bin/spire-agent /usr/bin/spire-agent && \
    ln -s /opt/spire/bin/spire-server /usr/bin/spire-server && \
    rm -rf spire-1.9.0-linux-amd64-musl.tar.gz
# Install python things (and rust temporarily)
RUN curl https://sh.rustup.rs -sSf -o rustup.sh && \
    chmod +x rustup.sh && \
    ./rustup.sh -y && \
    export PATH="$PATH:/root/.cargo/bin" && \
    pip install --no-cache-dir -r ./requirements.txt && \
    pip install --no-cache-dir git+https://github.com/HewlettPackard/py-spiffe.git@3640af9d6629c05e027f99010abc934cb74122a8 && \
    rm -r /root/.cargo /root/.rustup

# Set entrypoint
ENTRYPOINT [ "./entrypoint.sh" ]
