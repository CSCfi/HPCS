from paramiko.client import SSHClient
from paramiko import SSHException, AutoAddPolicy, RSAKey
from scp import SCPClient

# Hostname and port configuration
host = "lumi.csc.fi"
port = 22


def ssh_connect(username: str) -> SSHClient:
    """Create ssh connection

    Args:
        username (str): username
        hostname (str): hostname
        port (int): port

    Returns:
        SSHClient: The client connected to the host
    """

    # Create client, auth method
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()

    # Connect to host
    try:
        client.connect(host, port, username=username, auth_timeout=30, timeout=30)

    # Probably running in a container
    except SSHException:
        pkey = RSAKey.from_private_key_file("/tmp/.ssh/id_rsa")
        client.connect(
            host,
            port,
            username=username,
            pkey=pkey,
            look_for_keys=False,
            auth_timeout=30,
            timeout=30,
        )

    return client


def ssh_copy_file(client: SSHClient, source: str, destination: str) -> None:
    """Copy file to remote SSH

    Args:
        client (SSHClient): SSH Client
        source (str): Path to the source file
        destination (str): Path to the destination
    """

    # Open SCP Connection
    scp_client = SCPClient(client.get_transport(), socket_timeout=30)

    # Put file, exit
    scp_client.put(source, destination)


def distant_file_exists(client: SSHClient, path: str) -> bool:
    """Check that a distant file exists

    Args:
        client (SSHClient): SSH Client
        path (str): path to the file potentially existing file

    Returns:
        bool : wether the distant file exists or not
    """
    # Run check command
    stdin, stdout, stderr = ssh_run_command(client=client, command=f"stat {path}")

    # Close stdin
    stdin.close()

    # Check output
    if stderr.read().decode().find("No such file or directory") != -1:
        return False
    return True


def ssh_run_command(client: SSHClient, command: str, getPty=False):
    return client.exec_command(command=command, get_pty=getPty)
