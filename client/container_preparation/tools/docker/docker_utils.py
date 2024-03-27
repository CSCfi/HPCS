import docker, os


def check_build_env_exists(docker_client: docker.DockerClient):
    """Verify that the build environment (docker image sd-container/build_env) exists.

    Returns:
        bool: Wether or not the sd-container/build_env image exists.
    """
    # Check the build env exists
    try:
        return docker_client.images.get("sd-container/build_env")
    except docker.errors.ImageNotFound:
        return False


def build_build_env(docker_client: docker.DockerClient):
    """Builds the build environment"""
    docker_client.images.build(
        path=f"{os.path.realpath(os.path.dirname(__file__))}/build_env",
        dockerfile="./Dockerfile",
        tag="sd-container/build_env:latest",
    )


def check_docker_socket_access(docker_socket_path):
    """Checks wether or not the current user has access to the docker socket

    Args:
        docker_socket_path (string): The path to the docker running socket

    Returns:
        bool: Wether or not the user has access to the socket
    """
    groups = os.getgroups()
    if os.stat(docker_socket_path).st_gid in groups:
        return True
    return False
