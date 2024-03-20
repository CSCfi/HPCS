import argparse

# Parse arguments from the cli
def parse_arguments():
    """Parse arguments from cli

    Returns:
        ArgumentParser: the ArgumentParser produced
    """
    parser = argparse.ArgumentParser(description="CLI Optinons")

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="/tmp/hpcs-server.conf",
        help="Configuration file (INI Format) (default: /tmp/hpcs-server.conf)",
    )

    return parser.parse_args()