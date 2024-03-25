import argparse
from os.path import isfile, isdir

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

def check_arguments(input_path: str, output_path: str) -> bool:
    """Check cli arguments for data preparation and check wether or not input is a file

    Args:
        input_path (str): Path to the input file or directory
        output_path (str): Path to the output directory

    Returns:
        bool: Wether or not the input is a file
    """

    # Check input path exists, store wether it's a file or a directory
    try:
        input_is_file = isfile(input_path)
    except FileNotFoundError:
        print(f"File {input_path} doesn't exist.")

    # Check output path exists, and it's a directory
    try:
        isdir(input_path)
    except FileNotFoundError:
        print(f"Directory {output_path} doesn't exist.")

    return input_is_file