import platform, argparse, subprocess, requests


# Parse arguments from the cli
def parse_arguments():
    """Parse arguments from cli

    Returns:
        ArgumentParser: the ArgumentParser produced
    """
    parser = argparse.ArgumentParser(description="CLI Optinons")

    parser.add_argument(
        "--spire-trust-domain",
        "-t",
        type=str,
        default="lumi-sd-dev",
        help="Server address (default: lumi-sd-dev)",
    )
    parser.add_argument(
        "--sd-server-address",
        "-a",
        type=str,
        help="Server address",
    )
    parser.add_argument(
        "--spire-server-port",
        "-sp",
        type=int,
        default=10081,
        help="Spire server port (default: 10081)",
    )
    parser.add_argument(
        "--sd-server-port",
        "-ap",
        type=int,
        default=10080,
        help="SD API server port (default: 10080)",
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


def get_token(server, port, compute_node_token: bool):
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
        url = f"http://{server}:{port}/api/agents/token?hostname={hostname}"
    else:
        url = f"http://{server}:{port}/api/client/register"

    # Perform POST request to SD server
    response = requests.post(url)

    # Handle errors
    if response.status_code != 200 or response.json()["success"] != True:
        raise RuntimeError("Can't get token from API, aborting")
    return response.json()["token"]


if __name__ == "__main__":
    # Get arguments
    options = parse_arguments()

    # Get token from API
    token = get_token(
        options.sd_server_address, options.sd_server_port, options.compute_node
    )

    # Overwrite configuration template
    agent_configuration_template = open("./utils/agent-on-the-fly.conf").read()
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_TRUST_DOMAIN", options.spire_trust_domain
    )
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_SERVER_ADDRESS", options.sd_server_address
    )
    agent_configuration_template = agent_configuration_template.replace(
        "SPIRE_SERVER_PORT", str(options.spire_server_port)
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
