#!/bin/sh
#
## This entrypoint wraps the HPCS server with a spire agent
#

# export PYTHONPATH="${PYTHONPATH}:/server:/utils"

# Cleanup spire-agent generated files
end_entrypoint() {
	echo "Cleaning everything before leaving ..."
	rm -rf /tmp/data
	rm -r /tmp/spire-agent
	kill "$1"
	exit "$2"
}

# Reset spire data everytime
rm -rf /tmp/data

# Spawn spire agent with mounted configuration
spire-agent run -config /tmp/agent.conf || end_entrypoint 0 1 &
spire_agent_pid=$!

agent_socket_path=$(grep "socket_path" /tmp/agent.conf | cut -d "=" -f2 | cut -d '"' -f1)

RED='\033[0;31m'
NC='\033[0m'

sleep 10
until [ -e "${agent_socket_path}" ]; do
	printf "%b[LUMI-SD][Data preparation] Spire workload api socket doesn't exist, waiting 10 seconds %b" "${RED}" "${NC}\n"
	sleep 10
done

python3 ./app.py || end_entrypoint $spire_agent_pid 1

end_entrypoint $spire_agent_pid 0
