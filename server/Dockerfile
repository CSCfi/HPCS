# Using Python original Docker image
FROM --platform=linux/amd64 python:3.9-alpine

RUN apk add \
    git \
    build-base \
    openssl

# Install spire-agent
RUN wget -q https://github.com/spiffe/spire/releases/download/v1.9.0/spire-1.9.0-linux-amd64-musl.tar.gz
RUN tar xvf spire-1.9.0-linux-amd64-musl.tar.gz ; mv spire-1.9.0 /opt ; mv /opt/spire-1.9.0 /opt/spire
RUN ln -s /opt/spire/bin/spire-agent /usr/bin/spire-agent
RUN ln -s /opt/spire/bin/spire-server /usr/bin/spire-server

# Install pyspiffe package
RUN pip install git+https://github.com/HewlettPackard/py-spiffe.git

# Copy server
RUN mkdir /server
COPY ./server /server

# Install dependencies
RUN cd /server && pip install -r ./requirements.txt

# Copy utils
COPY ./utils /server/utils

# Set workdir
WORKDIR /server

# Set entrypoint
ENTRYPOINT [ "./entrypoint.sh" ]