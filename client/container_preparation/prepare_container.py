from tools.docker.docker_utils import check_docker_socket_access
from lib.image_build import build_prepared_image, create_sif_image
from tools.cli.cli import parse_arguments
from docker import DockerClient


if __name__ == "__main__":
    # Parse arguments from CLI
    arguments = parse_arguments()

    # For future usage
    base_image = arguments.base_oci_image
    sif_path = arguments.sif_path
    encrypted = arguments.encrypted
    docker_socket_path = arguments.docker_path

    # Checking the access to the docker socket - avoid waiting for an error to kill the program
    print(f"Checking the access to docker socket at {docker_socket_path}")
    if not check_docker_socket_access(docker_socket_path=docker_socket_path):
        print("No access to the docker socket, aborting")
        exit(1)

    # Create docker client for all the program
    docker_client = DockerClient(base_url=f"unix://{docker_socket_path}")

    # Will create the modified docker image, later used to create a Singularity/Apptainer image
    print("Building SD-CONTAINER ready OSI image")
    prepared_image_tag = build_prepared_image(
        base_image,
        docker_client=docker_client,
    )

    # Create the modified Singularity/Apptainer image (encrypted or not)
    print("Building SD-CONTAINER ready SIF image")

    # Commented out since we cannot run encrypted containers atm
    # if encrypted:
    #     print(
    #         "Encryption : to encrypt apptainer container, more capabilities are needed. Here are the additionnal flags added to the environment container cap_add=['MKNOD','SYS_ADMIN'], devices=['/dev/fuse'], security_opt=['apparmor:unconfined']"
    #     )
    create_sif_image(
        prepared_image_tag,
        destination_path=sif_path,
        docker_client=docker_client,
        docker_socket_path=docker_socket_path,
        encrypted=encrypted,
    )

    print(f"{sif_path}/{prepared_image_tag.split(':')[0]}.sif successfully created")
