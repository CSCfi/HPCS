import argparse
from re import search
from os import path
from pyspiffe.workloadapi import default_jwt_source, default_workload_api_client
from pyspiffe.spiffe_id import spiffe_id
from pyspiffe.exceptions import SpiffeIdError
from pyspiffe.svid.jwt_svid import JwtSvid
import requests
from vault.vault_utils import vault_login, write_secret
import yaml
from hashlib import sha512
from ssh_utils import ssh_connect, ssh_copy_file
from conf.client.conf import parse_configuration

# Provide client_id from cli$
# Same for trust domain
# Get image id and transform as for server
# Provide key path from cli
# All this to build used spiffeID


def parse_arguments() -> argparse.ArgumentParser:
    """Parse arguments from the cli

    Returns:
        ArgumentParser: Arguments parser with parsed arguments
    """
    parser = argparse.ArgumentParser(description="CLI Options")

    parser.add_argument(
        "--config",
        required=True,
        default="/tmp/hpcs-client.conf",
        help="Configuration file (INI Format) (default: /tmp/hpcs-client.conf)",
    )
    parser.add_argument(
        "--users",
        "-u",
        required=False,
        type=str,
        help="UNIX users that can access the key at the computing site, coma separated (Example : user1,user2,root)",
    )
    parser.add_argument(
        "--groups",
        "-g",
        required=False,
        type=str,
        help="UNIX groups that can access the key at the computing site, coma separated (Example : project_462000031,project_423000230,pepr_user)",
    )
    parser.add_argument(
        "--compute-nodes",
        "-c",
        required=True,
        type=str,
        help="Compute nodes that can access the key, coma separated (Example : cn01,cn02,cn03)",
    )
    parser.add_argument(
        "--pem-path",
        "-p",
        required=False,
        type=str,
        help="Path of the key to ship to the vault (Default : /tmp/keys)",
        default="/tmp/keys",
    )
    parser.add_argument(
        "--socketpath",
        "-s",
        required=False,
        type=str,
        help="Path to spire-agent socket (default: /tmp/agent.sock)",
        default="/tmp/agent.sock",
    )
    parser.add_argument(
        "--spiffeid",
        "-i",
        required=True,
        type=str,
        help="SpiffeID to use to connect to the vault (See spawn_agent.py)",
    )
    parser.add_argument(
        "--data-path",
        required=True,
        type=str,
        help="Path to the dataset to be published",
    )
    parser.add_argument(
        "--data-path-at-rest",
        required=True,
        type=str,
        help="Path to write the dataset on the supercomputer storage default :",
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Your username on the supercomputer",
    )

    return parser.parse_args()


def validate_options(options: argparse.ArgumentParser):
    """Check for the cli-provided options

    Args:
        options (argparse.ArgumentParser): The ArgumentParser coming from cli parsing

    Returns:
        Every options, re-parsed if needed
    """

    # Wether users or groups or both should be provided
    if not options.users and not options.groups:
        print(
            "Error, please provide at least one user or one group to give the access to the key"
        )
        options.print_help()
        exit(1)

    # Parse users, check that their names are are correctly formed (using UNIX regex's)
    users = options.users
    if users != None:
        users = options.users.split(",")
        for user in users:
            if not search("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", user):
                print(f"Error, invalid username {user}. Please provide valid usernames")
                exit(1)

    # Parse groups, check that their names are are correctly formed (using UNIX regex's)
    groups = options.groups
    if groups != None:
        groups = options.groups.split(",")
        for group in groups:
            if not search("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", group):
                print(
                    f"Error, invalid groupname {group}. Please provide valid groupnames"
                )
                exit(1)

    # Parse compute, check that their names are correctly formed (using UNIX regex's)
    compute_nodes = options.compute_nodes
    if compute_nodes != None:
        compute_nodes = options.compute_nodes.split(",")
        for compute_node in compute_nodes:
            if not search(
                "^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", compute_node
            ):
                print(
                    f"Error, invalid compute node name {compute_node}. Please provide valid compute node names"
                )
                exit(1)

    # Check that the keyfile exists
    if not path.exists(options.pem_path):
        print(f"Error, keyfile {options.pem_path} doesn't exist")
        exit(1)

    # Check that the datafile exists
    if not path.exists(options.pem_path):
        print(f"Error, datafile {options.data_path} doesn't exist")
        exit(1)

    # Check that spire-agent socket exists (workload API)
    if not path.exists(options.socketpath):
        print(f"Error, socketpath {options.socketpath} doesn't exist")
        exit(1)

    # Check that user provided spiffeID is well formed
    try:
        spiffeID = spiffe_id.SpiffeId().parse(f"{options.spiffeid}")
    except SpiffeIdError:
        print(f"Error, spiffeID {options.spiffeid} is malformed")
        exit(1)

    # Remove forbidden characters from dataset name to register it
    secret_name = options.data_path.split("/")[-1].replace("/", ".")

    return (
        users,
        groups,
        compute_nodes,
        options.pem_path,
        options.socketpath,
        spiffeID,
        secret_name,
        options.data_path,
        options.username,
    )


def create_authorized_workloads(
    SVID: JwtSvid, secret, url, users, groups, compute_nodes
):
    """Create workloads that are authorized to access to a secret

    Args:
        SVID (JwtSvid): Your SVID (for mTLS)
        application (str): The name of the application to give access to
        server (str): The SD server address
        port (number): The SD server port
        users ([str]): List of users in UNIX format, comma separated
        groups ([str]): List of groups in UNIX format, comma separated
        compute_nodes ([str]): List of compute nodes UNIX format, comma separated

    Returns:
        Data returned by the server (spiffeID to access the secret, this client's id, the path to the secret created workloads have access to)
    """

    # Prepare request
    url = f"{url}/api/client/create-workloads"
    payload = {
        "jwt": SVID.token,
        "secret": secret,
        "users": users,
        "groups": groups,
        "compute_nodes": compute_nodes,
    }

    # POST request
    response = requests.post(url, json=payload)

    # Handle errors
    if response.status_code != 200:
        print(
            f"Error while creating authorized workloads. Response code : {response.status_code}"
        )
        exit(1)

    # Print what happened if a response comes back from the server
    elif not response.json()["success"]:
        print("Error while creating authorized workloads")
        print(response.json()["message"])
        exit(1)

    # Success
    return (
        response.json()["spiffeID"],
        response.json()["clientID"],
        response.json()["secrets_path"],
        response.json()["user_role"],
    )


if __name__ == "__main__":
    # Parse arguments from CLI
    options = parse_arguments()    
    
    # Parse configuration file
    configuration = parse_configuration(options.config)

    # Validate / Parse them
    (
        users,
        groups,
        compute_nodes,
        pem_path,
        socketpath,
        spiffeID,
        secret_name,
        data_path,
        username,
    ) = validate_options(options)

    # Create the workloadAPI access
    jwt_workload_api = default_jwt_source.DefaultJwtSource(
        spiffe_socket_path=f"unix://{socketpath}",
        workload_api_client=None,
        timeout_in_seconds=None,
    )

    # Get the client's certificate to perform mTLS
    SVID = jwt_workload_api.get_jwt_svid(audiences=["TESTING"], subject=spiffeID)

    # Perform workloads authorization for the secret to be created
    users_spiffeID, client_id, secrets_path, user_role = create_authorized_workloads(
        SVID,
        secret_name,
        configuration["hpcs-server"]["url"],
        users,
        groups,
        compute_nodes,
    )

    # Login to the vault using client's certificate
    hvac_client = vault_login(configuration["vault"]["url"], SVID, f"client_{client_id}")

    # Prepare secret
    secret = {}
    with open(pem_path, "r") as pem:
        secret["key"] = pem.read()

    # Write secret to the vault
    write_secret(hvac_client, secrets_path, secret)

    print(
        f"Key successfully written to the vault. Users needs the role {user_role} to access the secret stored at {secrets_path}"
    )

    # Compute file's checksum
    checksum = sha512(open(options.data_path, "rb").read()).hexdigest()

    # Create SSH connection
    ssh_client = ssh_connect(username=username)

    # Ship data via SSH
    ssh_copy_file(ssh_client, data_path, options.data_path_at_rest)

    # Write datasets info object
    dataset_info_object = {
        "info": {
            "path_at_rest": f"{options.data_path_at_rest}/{data_path.split('/')[-1]}".replace(
                "//", "/"
            ),
            "secret_path": secrets_path,
            "access_role": user_role,
            "checksum": checksum,
            "spiffeID": str(users_spiffeID),
        },
    }

    # Write dataset info object to tempfile
    with open("/tmp/dataset_info.yaml", "w+") as dataset_info_file:
        dataset_info_file.write(yaml.dump(dataset_info_object))

    # Ship info file via SSH
    ssh_copy_file(
        ssh_client,
        "/tmp/dataset_info.yaml",
        f"{options.data_path_at_rest}/{secret_name}.info.yaml",
    )

    print(
        f"Data and info file were shipped to te supercomputer. Info about the dataset are available at {options.data_path_at_rest}/{secret_name}.info.yaml"
    )

    ssh_client.close()
