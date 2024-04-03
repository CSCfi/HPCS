import argparse


# Parse arguments from the cli
def parse_arguments() -> argparse.Namespace:
    """Parse arguments from cli

    Returns:
        ArgumentParser: the ArgumentParser produced
    """
    parser = argparse.ArgumentParser(description="CLI Options")

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        default="/tmp/hpcs-client.conf",
        help="Configuration file (INI Format) (default: /tmp/hpcs-client.conf)",
    )
    parser.add_argument(
        "--job-name",
        "-J",
        type=str,
        help="name of the job",
    )
    parser.add_argument(
        "--nodes",
        "-N",
        type=str,
        required=True,
        help="count of nodes on which to run",
    )
    parser.add_argument(
        "--partition",
        "-p",
        type=str,
        required=True,
        help="partition requested",
    )
    parser.add_argument(
        "--time",
        "-t",
        type=str,
        required=True,
        help="time limit",
    )
    parser.add_argument(
        "--account",
        "-A",
        type=str,
        required=True,
        help="account to bill the job to",
    )
    parser.add_argument(
        "--nodelist",
        "-w",
        type=str,
        required=True,
        help="request a specific list of hosts",
    )
    parser.add_argument(
        "--workdir",
        "-s",
        type=str,
        required=True,
        help="directory to work in (LUMI-SD specific -> different from chdir)",
    )
    parser.add_argument(
        "--application-info",
        "-ai",
        type=str,
        required=True,
        help="path to the info file for the image to run on supercomputer",
    )
    parser.add_argument(
        "--data-info",
        "-di",
        type=str,
        required=True,
        help="path to the info file for the dataset to use on supercomputer",
    )
    parser.add_argument(
        "--supplementary-input-scripts",
        "-i",
        type=str,
        required=True,
        help="path to your input verification scripts directory",
    )
    parser.add_argument(
        "--supplementary-output-scripts",
        "-o",
        type=str,
        required=True,
        help="path to your output verification scripts directory",
    )
    parser.add_argument(
        "--singularity-supplementary-flags",
        "-flags",
        type=str,
        help="supplementary arguments to pass to singularity",
    )
    parser.add_argument(
        "--arguments",
        "-args",
        type=str,
        help="supplementary arguments to pass to the application",
    )
    parser.add_argument(
        "--follow",
        "-f",
        action="store_true",
        help="Follow job's output (default : False)",
        default=False,
    )

    return parser.parse_args()


def check_arguments(options: argparse.Namespace) -> argparse.Namespace:

    if not options.job_name:
        options.job_name = f"lumi-sd_{options.username}"

    if len(options.time.split(":")) != 3:
        print(
            "Time format is wrong, please provide time limit in this format : HH:MM:SS"
        )

    return options
