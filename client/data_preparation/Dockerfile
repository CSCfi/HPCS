# Using Python original Docker image
FROM --platform=linux/amd64 python:3.9-alpine

# Install necessary packages
RUN apk add \
    git \
    curl \
    jq \
    build-base \
    libffi-dev

# Install Rust
RUN curl https://sh.rustup.rs -sSf -o rustup.sh ; chmod +x rustup.sh ; ./rustup.sh -y
ENV PATH="$PATH:/root/.cargo/bin"

# Install spire-agent

RUN wget -q https://github.com/spiffe/spire/releases/download/v1.9.1/spire-1.9.1-linux-amd64-musl.tar.gz
RUN tar xvf spire-1.9.1-linux-amd64-musl.tar.gz ; mv spire-1.9.1 /opt ; mv /opt/spire-1.9.1 /opt/spire
RUN ln -s /opt/spire/bin/spire-agent /usr/bin/spire-agent

# Install pyspiffe package
RUN pip install git+https://github.com/HewlettPackard/py-spiffe.git@3640af9d6629c05e027f99010abc934cb74122a8

# Create code directory, output directory
RUN mkdir /data_preparation /output

# Copy useful data from the project
COPY ./client/data_preparation /data_preparation

# Install dependencies
RUN cd /data_preparation && pip install -r ./requirements.txt

# Copy utils for SPIFFEID creation ...
COPY ./utils /data_preparation/utils

# Set workdir
WORKDIR /data_preparation

# Set entrypoint
ENTRYPOINT [ "./entrypoint.sh" ]
