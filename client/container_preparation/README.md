# Introduction
This directory contains code which prepares existing OCI images to be used on LUMI in a secure way.
The code adds layers to handle encryption and encrypts the resulting apptainer (singularity) image itself.

## Current state

Currently, the container_preparation.py script is able to run most of the needed tasks
- Create a new receipe (Dockerfile) prepared for secure workloads
- Build the new image
- Build an apptainer image based on the just built one
    - Unencrypted
    - But unfortunately not encrypted for the moment


What is missing :
- Encryption of the container
- Crypt binary inside of the resulting container and the logic needed to encrypt ouput data before leaving the container
- Documentation (global) - Explanation of how it works, what is needed ...
