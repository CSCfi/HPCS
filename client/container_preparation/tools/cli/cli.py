import argparse


# Parse arguments from the cli
def parse_arguments() -> argparse.ArgumentParser:
    """Parse arguments from the cli

    Returns:
        ArgumentParser: Arguments parser with parsed arguments
    """
    parser = argparse.ArgumentParser(description="CLI Options")

    parser.add_argument(
        "--base-oci-image", "-b", required=True, type=str, help="Base OCI image"
    )
    parser.add_argument(
        "--sif-path",
        "-s",
        required=True,
        type=str,
        help='Path for the final SIF image (please use "$(pwd)" instead of ".")',
    )
    parser.add_argument(
        "--encrypted",
        "-e",
        action="store_true",
        help="Encrypt final SIF image or not (default : False)",
        default=False,
    )
    parser.add_argument(
        "--docker-path",
        "-d",
        type=str,
        help="Path to the docker socket (default : /var/run/docker.sock)",
        default="/var/run/docker.sock",
    )
    parser.add_argument(
        "--docker-host-path",
        type=str,
        help="Path to the docker socket on the host (default : /var/run/docker.sock)",
        default="/var/run/docker.sock",
    )
    parser.add_argument(
        "--sif-host-path",
        type=str,
        help="Path to the SIF directory on the host (default : same as --sif-path). Use this when running in a container with volume mounts",
        default=None,
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite existing SIF image (default : True)",
        default=True,
    )

    return parser.parse_args()
