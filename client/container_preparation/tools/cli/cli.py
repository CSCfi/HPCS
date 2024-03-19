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

    return parser.parse_args()
