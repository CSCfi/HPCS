import hashlib, sys, os
from quart import Quart, jsonify, request
from lib.spire_interactions import (
    token_generate,
    entry_create,
    get_server_identity_JWT,
    validate_client_JWT_SVID,
)
from lib import spire_interactions
from tools.docker_utils import get_build_env_image_digests
from pyspiffe.spiffe_id.spiffe_id import SpiffeId
from pyspiffe.workloadapi import default_jwt_source

from tools.config.config import parse_configuration
from tools.cli.cli import parse_arguments
from utils.vault.vault_utils import (
    vault_login,
    write_client_policy,
    write_client_role,
    write_user_policy,
    write_user_role,
)

app = Quart(__name__)

options = parse_arguments()
configuration = parse_configuration(options.config)

if configuration["spire-server"].get("spire-server-bin"):
    spire_interactions.spire_server_bin = configuration["spire-server"][
        "spire-server-bin"
    ]

if configuration["spire-agent"].get("spire-agent-socket"):
    spire_interactions.jwt_workload_api = default_jwt_source.DefaultJwtSource(
        workload_api_client=None,
        spiffe_socket_path=f"unix://{configuration['spire-agent'].get('spire-agent-socket')}",
        timeout_in_seconds=None,
    )

else:
    spire_interactions.jwt_workload_api = default_jwt_source.DefaultJwtSource(
        workload_api_client=None,
        spiffe_socket_path="unix:///tmp/spire-agent/public/api.sock",
        timeout_in_seconds=None,
    )

if configuration["spire-agent"].get("hpcs-server-spiffeid"):
    spire_interactions.hpcs_server_spiffeid = configuration["spire-agent"].get(
        "hpcs-server-spiffeid"
    )

if configuration["spire-server"].get("socket-path"):
    spire_interactions.spire_server_socketpath = configuration["spire-server"].get(
        "socket-path"
    )

if configuration["spire-server"].get("pre-command"):
    spire_interactions.pre_command = configuration["spire-server"]["pre-command"]
    if configuration["spire-server"]["pre-command"] == '""':
        spire_interactions.pre_command = ""

# Defining the trust domain (SPIRE Trust Domain)
trust_domain = configuration["spire-server"]["trust-domain"]

# Perform vault login, to be able to run later operations against vault
hvac_client = vault_login(
    configuration["vault"]["url"],
    get_server_identity_JWT(),
    configuration["vault"]["server-role"],
)


# Dummy endpoint that handles the registration of compute nodes.
# TODO: Develop a SPIRE plugin that handles this better than this dummy endpoint
# THIS ENDPOINT SHOULD BE REMOVED, IT DOESN'T CERTIFY ANYHTING, IT WILL PROVIDE AN IDENTITY TO ANYONE ASKING FOR
@app.route("/api/agents/token", methods=["POST"])
async def handle_dummy_token_endpoint():

    # Read hostname from parameters
    hostname = request.args.get("hostname")
    if hostname != None:

        # Create spiffeID based on the hostname
        spiffeID = SpiffeId(f"spiffe://{trust_domain}/h/{hostname}")

        # Associate a token to the spiffeID
        result = token_generate(spiffeID)
        if result.returncode == 0:

            # Return the agent and the spiffeID to the node
            return {
                "success": True,
                "message": "spiffeID created, token expires in 60 seconds",
                "spiffeID": str(spiffeID),
                "token": result.stdout.decode().split(": ")[1].replace("\n", ""),
            }

        result.stdout

    # Error
    return {
        "success": False,
        "message": "Please provide the hostname bound to the token.",
    }


# Get an agent configuration out of a client request
# TODO: Handle a case in which we would have "certified application providers"
# In this case, we could think of a "securely provided" x509 certificates, provided by a 3rd party
# This could lead to not-needing this endpoint for "certified application providers"
@app.route("/api/client/register", methods=["POST"])
async def handle_client_registration():

    # Generate a client id out of it's IP address (SHA256 the ip, cut it to 10 characters)
    client_id = request.headers.get("Remote-Addr")
    client_id = hashlib.sha256(client_id.encode()).hexdigest()[0:9]

    # Write a policy to the vault to authorize the client to write secrets
    write_client_policy(hvac_client, f"client_{client_id}")

    # Create spiffeID out of this client id
    agent_spiffeID = SpiffeId(f"spiffe://{trust_domain}/c/{client_id}")

    # Generate a token to register the agent (again, based on the client id)
    result = token_generate(agent_spiffeID)

    if result.returncode == 0:

        # Parse token
        agent_token = result.stdout.decode().split(": ")[1].replace("\n", "")

        # Create a spiffeID for the workloads on the client.
        # Register workloads that have to run on this agent
        workload_spiffeID = SpiffeId(f"spiffe://{trust_domain}/c/{client_id}/workload")

        # Write the role bound to the workload's spiffeID
        write_client_role(hvac_client, f"client_{client_id}", workload_spiffeID)

        # For each authorized container preparation process (Here, a list of docker container_preaparation image names)
        for digest in get_build_env_image_digests():
            digest = digest.replace("\n", "")
            workload_selector = f"docker:image_id:{digest}"

            # Register a workload bound to the agent, and the workload (Here, a container image)
            result = entry_create(
                agent_spiffeID, workload_spiffeID, [workload_selector]
            )

            # Do not stop if entry already exists, stop for any other error
            if result == None or not result.stderr.decode().find(
                "similar entry already exists"
            ):
                return {
                    "success": False,
                    "message": "token created, it expires in 60 seconds. An error occured while registering workloads.",
                    "client_id": client_id,
                    "token": agent_token,
                }

        # Spire-Agent binary
        result = entry_create(
            agent_spiffeID,
            workload_spiffeID,
            [
                "unix:sha256:5ebff0fdb3335ec0221c35dcc7d3a4433eb8a5073a15a6dcfdbbb95bb8dbfa8e"
            ],
        )

        # Python 3.9 binary
        result = entry_create(
            agent_spiffeID,
            workload_spiffeID,
            [
                "unix:sha256:956a50083eb7a58240fea28ac52ff39e9c04c5c74468895239b24bdf4760bffe"
            ],
        )

        # Qemu x86_64 (For docker mac) // Could add Rosetta binary
        result = entry_create(
            agent_spiffeID,
            workload_spiffeID,
            [
                "unix:sha256:3fc6c8fbd8fe429b67276854fbb5ae594118f7f0b10352a508477833b04ee9b7"
            ],
        )

        # Success
        return {
            "success": True,
            "message": "token created,it expires in 60 seconds. Workloads have been registered too.",
            "client_id": client_id,
            "spiffeID": str(agent_spiffeID),
            "token": agent_token,
        }

    # Error
    return {
        "success": "false",
        "message": "Error while creating agent's token",
    }


# Endpoint to register proper spiffeIDs to give access to a secret.
# It necessitate :
# - A JWT SVID to perform mTLS
# - The name of the application to give access to
# - A list of compute nodes that will get access to the secret
# - A list of users or groups or both that will get access to the secret on the selected nodes
@app.route("/api/client/create-workloads", methods=["POST"])
async def handle_workload_creation():
    # Get data from request synchronously
    data = await request.get_json()

    # Generate a client id out of it's IP address (SHA256 the ip, cut it to 10 characters)
    client_id = request.headers.get("Remote-Addr")
    client_id = hashlib.sha256(client_id.encode()).hexdigest()[0:9]

    # Parse the spiffeID that will access the application
    spiffeID = SpiffeId(f"spiffe://{trust_domain}/c/{client_id}/s/{data['secret']}")

    # Check that the SVID correspond to the client_id (Can be removed if developper is certified)
    if validate_client_JWT_SVID(data["jwt"], client_id):

        # List of treated compute nodes
        compute_nodes_added = {}
        for compute_node in data["compute_nodes"]:
            # Lists of groups and users treated for the compute node
            compute_nodes_added[compute_node] = {}
            users_added = []
            groups_added = []

            # Compute node's agent spiffeID
            parentID = SpiffeId(f"spiffe://{trust_domain}/h/{compute_node}")

            # For each user
            if data["users"] != None:
                for user in data["users"]:

                    # Create proper selector
                    selectors = [f"unix:user:{user}"]

                    # Register it with the current compute node as parent
                    result = entry_create(parentID, spiffeID, selectors)

                    # If an error occurs when creating entry and the entry wasn't created
                    if result == None or not result.stderr.decode().find(
                        "similar entry already exists"
                    ):
                        # Error
                        return {
                            "success": False,
                            "message": f"error occured while registering a workload : {str(spiffeID)}. Registered selectors available in compute_nodes_added subobject.",
                            "clientID": client_id,
                            "spiffeID": str(spiffeID),
                            "compute_nodes_added": compute_nodes_added,
                        }

                    # Note user as treated
                    users_added.append(user)

            # For each group
            if data["groups"] != None:
                for group in data["groups"]:

                    # Create proper selector
                    selectors = [f"unix:supplementary_group:{group}"]

                    # Register it with the current compute node as parent
                    result = entry_create(parentID, spiffeID, selectors)

                    # If an error occurs when creating entry and the entry wasn't created
                    if result == None or not result.stderr.decode().find(
                        "similar entry already exists"
                    ):
                        # Error
                        return {
                            "success": False,
                            "message": f"error occured while registering a workload : {str(spiffeID)}. Registered selectors available in compute_nodes_added subobject.",
                            "clientID": client_id,
                            "spiffeID": str(spiffeID),
                            "compute_nodes_added": compute_nodes_added,
                        }

                    # Note group as treated
                    groups_added.append(group)

            # Store groups and users treated under the compute node for which they have been
            compute_nodes_added[compute_node]["users"] = users_added
            compute_nodes_added[compute_node]["groups"] = groups_added

        # Generate and create a policy that gives read-only access to the application's secret
        write_user_policy(hvac_client, f"client_{client_id}", data["secret"])

        # Generate and create a role bound to the policy and to the spiffeID
        write_user_role(hvac_client, f"client_{client_id}", data["secret"], spiffeID)

        # Success
        return {
            "success": True,
            "message": "successfully registered spiffeID, policy and role",
            "clientID": client_id,
            "spiffeID": str(spiffeID),
            "compute_nodes_added": compute_nodes_added,
            "secrets_path": f"client_{client_id}/{data['secret']}",
            "user_role": f"client_{client_id}-{data['secret']}",
        }

    # Error
    return {
        "success": False,
        "message": "your SVID doesn't match to your client_id. Please ensure this identity belongs to you",
    }


if __name__ == "__main__":
    app.run(port=10080, host="0.0.0.0")
