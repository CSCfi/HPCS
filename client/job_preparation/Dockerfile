# Using Python original Docker image
FROM --platform=linux/amd64 python:3.9-alpine

# Install necessary packages
RUN apk add \
    curl \
    build-base \
    libffi-dev

RUN curl https://sh.rustup.rs -sSf -o rustup.sh ; chmod +x rustup.sh ; ./rustup.sh -y
ENV PATH="$PATH:/root/.cargo/bin"

# Create code directory, output directory
RUN mkdir /job_preparation

# Copy useful data from the project
COPY ./client/job_preparation /job_preparation

# Copy utils for SPIFFEID creation ...
COPY ./utils /job_preparation/utils

# Install dependencies
RUN cd /job_preparation && pip install -r ./requirements.txt

# Set workdir
WORKDIR /job_preparation

# Set entrypoint
ENTRYPOINT [ "python3", "./prepare_job.py" ]