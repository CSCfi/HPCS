# Using Python original Docker image
FROM python:3.9-bullseye

# Update & Upgrade global packages base
RUN apt update -y \
	&& apt upgrade -y

# Install necessary packages
RUN apt install -y \
    git \
    curl \
    jq

# Install spire-agent
RUN wget -q https://github.com/spiffe/spire/releases/download/v1.9.0/spire-1.9.0-linux-amd64-musl.tar.gz
RUN tar xvf spire-1.9.0-linux-amd64-musl.tar.gz ; mv spire-1.9.0 /opt ; mv /opt/spire-1.9.0 /opt/spire
RUN ln -s /opt/spire/bin/spire-agent /usr/bin/spire-agent

# Install pyspiffe package
RUN pip install git+https://github.com/HewlettPackard/py-spiffe.git

# Create code directory, output directory
RUN mkdir /container_preparation /output ; chmod -R 777 /output

# Copy useful data from the project
COPY ./client/container_preparation /container_preparation

# Install dependencies
RUN cd /container_preparation && pip install -r ./requirements.txt

# Copy utils for SPIFFEID creation ...
COPY ./utils /container_preparation/utils

# Set workdir
WORKDIR /container_preparation

# Set entrypoint
ENTRYPOINT [ "./entrypoint.sh" ]
