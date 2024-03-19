FROM ubuntu:22.04

# Update & Upgrade global packages base
RUN apt update -y \
	&& apt upgrade -y


# Install dependencies
RUN apt install \
	-y wget \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools

RUN DEBIAN_FRONTEND=noninteractive apt install -y cryptsetup

# Get apptainer installer and install it
RUN wget -q https://github.com/apptainer/apptainer/releases/download/v1.2.5/apptainer_1.2.5_amd64.deb
RUN apt install -y ./apptainer_1.2.5_amd64.deb

# Create a directory to eventually map for output image
RUN mkdir /output

# Creating an all permission directory to work
RUN mkdir /home/user
RUN chmod -R 777 /home/user
WORKDIR /home/user

ENTRYPOINT [ "apptainer", "build" ]
