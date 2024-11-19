# Container preparation

Using the cli directly isn't recommended, the supported way is through docker's entrypoint.

The container preparation cli allows the user to create/encrypt/ship a HPCS ready image based on any OCI image.

```
usage: prepare_container.py [-h] --base-oci-image BASE_OCI_IMAGE --sif-path SIF_PATH [--encrypted] [--docker-path DOCKER_PATH]

CLI Options

options:
  -h, --help            show this help message and exit
  --base-oci-image BASE_OCI_IMAGE, -b BASE_OCI_IMAGE
                        Base OCI image
  --sif-path SIF_PATH, -s SIF_PATH
                        Path for the final SIF image (please use "$(pwd)" instead of ".")
  --encrypted, -e       Encrypt final SIF image or not (default : False)
  --docker-path DOCKER_PATH, -d DOCKER_PATH
                        Path to the docker socket (default : /var/run/docker.sock)
```

Examples

```bash
# Show the help above
python3 ./client/container_preparation/prepare_container.py --help

# Run the container preparation while specifying every parameters
python3 ./client/container_preparation/prepare_container.py --base-oci-image talinx/jp2a --sif-path $(pwd) --encrypted --docker-path /var/run/docker.sock

# Run the container preparation while specifying every parameters (shortened version)
python3 ./client/container_preparation/prepare_container.py -b talinx/jp2a -s $(pwd) -e -d /var/run/docker.sock

# Run the container preparation specifying minimum flags
python3 ./client/container_preparation/prepare_container.py -b talin/jp2a -s $(pwd)
```
