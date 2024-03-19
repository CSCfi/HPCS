import argparse


# Parse arguments from the cli
def parse_arguments() -> argparse.ArgumentParser:
    """Parse arguments from the cli

    Returns:
        ArgumentParser: Arguments parser with parsed arguments
    """
    parser = argparse.ArgumentParser(description="CLI Options")

    parser.add_argument(
        "--input-path", "-i", required=True, type=str, help="Path to the input data"
    )
    parser.add_argument(
        "--output-path",
        "-o",
        required=True,
        type=str,
        help="Path to the output encrypted data",
    )

    return parser.parse_args()
