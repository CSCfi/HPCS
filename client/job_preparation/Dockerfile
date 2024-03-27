# Using Python original Docker image
ARG  BUILDPLATFORM=linux/amd64
FROM --platform=$BUILDPLATFORM python:3.9-alpine

# Copy useful data from the project
COPY ./client/job_preparation /job_preparation

# Set workdir
WORKDIR /job_preparation

# Copy utils for SPIFFEID creation ...
COPY ./utils /job_preparation/utils

# Install necessary packages and rust
RUN apk add --no-cache \
    curl=8.5.0-r0 \
    build-base=0.5-r3 \
    libffi-dev=3.4.4-r3 && \
curl https://sh.rustup.rs -sSf -o rustup.sh ; chmod +x rustup.sh ; ./rustup.sh -y ; export PATH="$PATH":/root/.cargo/bin && \
pip install --no-cache-dir -r ./requirements.txt && \
rm -r /root/.cargo /root/.rustup

# Set entrypoint
ENTRYPOINT [ "python3", "./prepare_job.py" ]
