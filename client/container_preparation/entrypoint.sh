#!/bin/sh
#
## This entrypoint wraps up the container preparation with the agent spawning and the key shipping.
#

# Default values for arguments
docker_path="/var/run/docker.sock"

# Argument parser, arguments for both container preparation and key shipping should be handled here.
parse_args() {
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -b|--base-oci-image) base_oci_image="$2"; shift 2 ;;
            -s|--sif-path) sif_path="$2"; shift 2 ;;
            -e|--encrypted) encrypted=true; shift ;;
            --data-path) data_path="$2"; shift 2 ;;
            --data-path-at-rest) data_path_at_rest="$2"; shift 2 ;;
            --username) username="$2"; shift 2 ;;
            -u|--users) users="$2" ; shift 2 ;;
            -g|--groups) groups="$2" ; shift 2 ;;
            -c|--compute-nodes) compute_nodes="$2" ; shift 2 ;;
            -d|--docker-path) docker_path="$2" ; shift 2 ;;
            -h|--help) python3 ./prepare_container.py --help ; python3 ./utils/ship_a_key.py --help ; exit 0 ;;
            *) echo "Error: Unknown option $1"; python3 ./prepare_container.py --help ; python3 ./utils/ship_a_key.py --help ; exit 1 ;;
        esac
    done

    # Check for required arguments
    if [ -z "$base_oci_image" ] || [ -z "$sif_path" ] || [ -z "$data_path" ] || [ -z "$data_path_at_rest" ] || ( [ -z "$users" ] && [ -z "$groups" ] ) || [ -z "$compute_nodes" ]; then
        echo echo "Please provides options for both of these programs : "
        python3 ./prepare_container.py --help
        python3 ./utils/ship_a_key.py --help
        exit 1
    fi
}

# Cleanup spire-agent generated files
end_entrypoint() {
    if ! [ -n "$encrypted" ]; then
        echo "No encryption, nothing to clean"
    else
        echo "Cleaning everything before leaving ..."
        rm -rf /tmp/data
        rm /tmp/agent*
        rm -f /tmp/keys
        rm /tmp/dataset_info.yaml
        kill "$1"
    fi
    exit "$2"
}

# Colors for prints
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments from cli
parse_args "$@"

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Entering entrypoint"

#
## [RUN] Perform node attestation (spawn agent, register it's and it's workload's spiffeID)
#

if [ -n "$encrypted" ]; then
    echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Encryption mode is on. Registering and running SPIRE Agent"

    python3 ./utils/spawn_agent.py > /dev/null 2> /dev/null || exit 1 &
    spire_agent_pid=$!

fi

#
## [END] Perform node attestation
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Run container preparation"

#
## [RUN] Run container preparation (Preparation of new image, build of new image, build of Apptainer/Singularity image)
#

if [ -z "$encrypted" ]; then
    python3 ./prepare_container.py -b "$base_oci_image" -s "$sif_path" -d "$docker_path" || end_entrypoint "$spire_agent_pid" 1
else
    python3 ./prepare_container.py -e -b "$base_oci_image" -s "$sif_path"  -d "$docker_path" || end_entrypoint "$spire_agent_pid" 1
fi

#
## [END] Run container preparation
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Container preparation ended"

#
## [RUN] Ship private key to the vault (Creation of workload identity to give access to the key, writing key to the vault)
#

if [ -n "$encrypted" ]; then
    spiffeID=$(spire-agent api fetch --output json -socketPath /tmp/agent.sock | jq '.svids[0].spiffe_id' -r)
fi


if [ -z "$encrypted" ]; then
    echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Encryption mode is off, nothing to do"

else
    echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Encryption mode is on, writing key to the vault, using spiffeID $spiffeID"

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

    echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Key written to the vault"
fi

#
## [END] Ship private key to the vault
#

echo -e "${YELLOW}[LUMI-SD]${NC}${BLUE}[Container preparation]${NC} Leaving entrypoint"

end_entrypoint "$spire_agent_pid" 0
