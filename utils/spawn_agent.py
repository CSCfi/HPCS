import platform, argparse, subprocess, requests
from conf.client.conf import parse_configuration


# Parse arguments from the cli
def parse_arguments():
    """Parse arguments from cli

    Returns:
        ArgumentParser: the ArgumentParser produced
    """
    parser = argparse.ArgumentParser(description="CLI Options")

    parser.add_argument(
        "--config",
        required=True,
        default="/tmp/hpcs-client.conf",
        help="Configuration file (INI Format) (default: /tmp/hpcs-client.conf)",
    )
    parser.add_argument(
        "--socketpath",
        "-s",
        type=str,
        default="/tmp/agent.sock",
        help="Destination path for spire-agent socket (default: /tmp/agent.sock)",
    )
    parser.add_argument(
        "--compute-node",
        "-cn",
        action="store_true",
        default=False,
        help="Are you seeking for a token for a client agent (False ( -> don't put anything)) or a running node agent ? (True ( -> put -cn))",
    )

    return parser.parse_args()


def get_token(url, compute_node_token: bool):
    """Get joinToken to perform node registration from server

    Args:
        server (str): SD server address
        port (str): SD server port
        compute_node_token (bool): wether we are registering a compute node or a client

    Raises:
        RuntimeError: raises when unable to fetch token from SD server

    Returns:

    """

    # Check wether we are performing compute node attestation or client attestation, create url
    if compute_node_token:
        hostname = platform.node()
        url = f"{url}/api/agents/token?hostname={hostname}"
    else:
        url = f"{url}/api/client/register"

    # Perform POST request to SD server
    response = requests.post(url)

    # Handle errors
    if response.status_code != 200 or response.json()["success"] != True:
        raise RuntimeError("Can't get token from API, aborting")
    return response.json()["token"]


if __name__ == "__main__":
    # Get arguments
    options = parse_arguments()

    # Parse configuration file
    configuration = parse_configuration(options.config)

    # Get token from API
    token = get_token(configuration["hpcs-server"]["url"], options.compute_node)

    # Overwrite configuration template
    agent_configuration_template = open("./utils/agent-on-the-fly.conf").read()
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_TRUST_DOMAIN", configuration["spire-server"]["trust-domain"]
    )
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_SERVER_ADDRESS", configuration["spire-server"]["address"]
    )
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_SERVER_PORT", configuration["spire-server"]["port"]
    )
    agent_configuration_template = agent_configuration_template.replace(
        "SOCKETPATH", options.socketpath
    )
    agent_configuration_template = agent_configuration_template.replace(
        "JOIN_TOKEN", token
    )

    # Write configuration
    with open("/tmp/agent.conf", "w+") as conf:
        conf.write(agent_configuration_template)

    # Register the command
    command = f"spire-agent run -config /tmp/agent.conf -logFile /tmp/agent.log".split(
        " "
    )

    print(command)

    # Run agent
    subprocess.run(command, cwd="/tmp")
