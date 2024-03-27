import argparse
from paramiko import SSHClient
import yaml
import sys, os

sys.path.append(os.path.expanduser("../../../"))  # For cli usage
sys.path.append(os.path.expanduser("../../"))  # For inside-container usage
from utils.ssh_utils import distant_file_exists, ssh_run_command


def get_info_from_infofile(ssh_client: SSHClient, path: str):
    """Gather information from an info file

    Args:
        ssh_client (SSHClient): ssh client to use to read info file
        path (str): path to the info file on distant server

    Returns:
        Path of the file at rest,
        spiffeID to have to decrypt the data,
        Vault access role to use to access the key,
        Path to the key in vault
    """

    # Parse info file
    info = parse_info_file(ssh_client, path)

    # Verify that data exists
    if distant_file_exists(client=ssh_client, path=info["path_at_rest"]):
        if check_file_checksum(
            ssh_client=ssh_client, path=info["path_at_rest"], checksum=info["checksum"]
        ):
            return (
                info["path_at_rest"],
                info["spiffeID"],
                info["access_role"],
                info["secret_path"],
            )
        else:
            print("Checksum is wrong, aborting")
            exit(1)


def parse_info_file(ssh_client: SSHClient, path: str):
    """Read an info file and parse it as a Python object

    Args:
        ssh_client (SSHClient): ssh client to use to read info file
        path (str): path to the info file on distant server

    Returns:
        Object: Python object corresponding to the info file's info
    """
    if distant_file_exists(ssh_client, path):
        # Get the content of the info file
        stdin, stdout, stderr = ssh_run_command(ssh_client, f"cat {path}")

        # Close stdin
        stdin.close()

        # Parse info file
        info = stdout.read().decode()
        info = yaml.safe_load(info)
        return info["info"]

    else:
        print(f"Error while reading infofile {path} :")
        exit(1)


def check_file_checksum(ssh_client: SSHClient, path: str, checksum: str) -> bool:
    """Compare the checksum of a file with the checksum provided as a parameter

    Args:
        ssh_client (SSHClient): ssh client to use to read info file
        path (str): path to the file to checksum on distant server
        checksum (str): checksum to compare the computed one with

    Returns:
       bool : wether the checksum provided correspond to the file at `path`
    """
    # Run checksum on the data file
    stdin, stdout, stderr = ssh_run_command(
        client=ssh_client, command=f"sha512sum {path}"
    )
    stdin.close()

    # Compare it with the provided checksum
    computed_checksum = stdout.read().decode().split(" ")[0]
    if computed_checksum != checksum:
        return False
    return True
