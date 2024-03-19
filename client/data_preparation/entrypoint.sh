#!/bin/sh
#
## This entrypoint wraps up the Data preparation with the agent spawning and the key shipping.
#

# Argument parser, arguments for both Data preparation and key shipping should be handled here.
parse_args() {
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -i|--input-data) input_data="$2"; shift 2 ;;
            -o|--output-data) output_data="$2"; shift 2 ;;
            --data-path) data_path="$2"; shift 2 ;;
            --data-path-at-rest) data_path_at_rest="$2"; shift 2 ;;
            --username) username="$2"; shift 2 ;;
            -u|--users) users="$2" ; shift 2 ;;
            -g|--groups) groups="$2" ; shift 2 ;;
            -c|--compute-nodes) compute_nodes="$2" ; shift 2 ;;
            -h|--help) python3 ./prepare_container.py --help ; python3 ./utils/ship_a_key.py --help ; exit 0 ;;
            *) echo "Error: Unknown option $1"; python3 ./prepare_data.py --help ; python3 ./utils/ship_a_key.py --help ; exit 1 ;;
        esac
    done

    # Check for required arguments
    if [ -z "$input_data" ] || [ -z "$output_data" ] || [ -z "$data_path" ] || [ -z "$data_path_at_rest" ] || [ -z "$username" ] || ( [ -z "$users" ] && [ -z "$groups" ] ) || [ -z "$compute_nodes" ]; then
        echo echo "Please provides options for both of these programs : "
        python3 ./prepare_data.py --help
        python3 ./utils/ship_a_key.py --help
        exit 1
    fi
}

# Cleanup spire-agent generated files
end_entrypoint() {
    echo "Cleaning everything before leaving ..."
    rm -rf /tmp/data
    rm /tmp/agent*
    rm -f /tmp/keys
    rm /tmp/dataset_info.yaml
    kill "$1"
    exit "$2"
}

# Colors for prints
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments from cli
parse_args "$@"

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Entering entrypoint"

#
## [RUN] Perform node attestation (spawn agent, register it's and it's workload's spiffeID)
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Registering and running SPIRE Agent"

python3 ./utils/spawn_agent.py > /dev/null 2> /dev/null || exit 1  &
spire_agent_pid=$!

until [ -e /tmp/agent.sock ]
do
    echo -e "${RED}[LUMI-SD][Data preparation] Spire workload api socket doesn't exist, waiting 10 seconds ${NC}"
    sleep 10
done

#
## [END] Perform node attestation
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Run Data preparation"

#
## [RUN] Run Data preparation (Encryption of input data)
#

python3 ./prepare_data.py -i "$input_data" -o "$output_data" || end_entrypoint "$spire_agent_pid" 1

#
## [END] Run Data preparation
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Data preparation ended"

#
## [RUN] Ship private key to the vault (Creation of workload identity to give access to the key, writing key to the vault)
#

spiffeID=$(spire-agent api fetch --output json -socketPath /tmp/agent.sock | jq '.svids[0].spiffe_id' -r)


echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Writing key to the vault, using spiffeID $spiffeID"

# Handle different cases of user provided compute nodes / user / groups
if [ -z "$users" ]; then
    # If the user provided only groups
    python3 ./utils/ship_a_key.py --username "$username" -g "$groups" -c "$compute_nodes" --data-path "$data_path" --data-path-at-rest "$data_path_at_rest" -i "$spiffeID" || end_entrypoint "$spire_agent_pid" 1
elif [ -z "$groups" ] ; then
    # If the user provided only users
    python3 ./utils/ship_a_key.py --username "$username" -u "$users" -c "$compute_nodes" --data-path "$data_path" --data-path-at-rest "$data_path_at_rest" -i "$spiffeID" || end_entrypoint "$spire_agent_pid" 1
else
    # If the user provided both
    python3 ./utils/ship_a_key.py --username "$username" -u "$users" -g "$groups" -c "$compute_nodes" --data-path "$data_path" --data-path-at-rest "$data_path_at_rest" -i "$spiffeID" || end_entrypoint "$spire_agent_pid" 1
fi

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Key written to the vault"

#
## [END] Ship private key to the vault
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Data preparation]${NC} Leaving entrypoint"

end_entrypoint "$spire_agent_pid" 0
