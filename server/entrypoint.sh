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

agent_socket_path=$(cat /tmp/agent.conf | grep "socket_path" | cut -d "=" -f2 | cut -d "\"" -f1)

sleep 10
until [ -e $agent_socket_path ]
do
    echo -e "${RED}[LUMI-SD][Data preparation] Spire workload api socket doesn't exist, waiting 10 seconds ${NC}"
    sleep 10
done

python3 ./app.py || end_entrypoint $spire_agent_pid 1

end_entrypoint $spire_agent_pid 0