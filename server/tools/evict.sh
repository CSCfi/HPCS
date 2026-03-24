#!/bin/sh
#
# evict.sh — Evict SPIRE agents or delete SPIRE entries from the hpcs-stack deployment.
#
# Usage:
#   evict.sh agents  [--all | --jq-selector <jq>] [--verbose]
#   evict.sh entries [--all | --jq-selector <jq>] [--verbose]
#
# --all              Select all agents/entries
# --jq-selector      A jq expression producing one ID per line from the JSON list output.
#                    For agents:  input is `spire-server agent list -output json`
#                                 expression should yield agent path, e.g. '.agents[].id.path'
#                    For entries: input is `spire-server entry show -output json`
#                                 expression should yield entry ID, e.g. '.entries[].id'
# --verbose          Print each successful eviction/deletion, and any failures with detail
#
# Examples:
#   evict.sh agents --all --verbose
#   evict.sh entries --all
#   evict.sh entries --jq-selector '.entries[] | select(.selectors[].value | startswith("user:")) | .id' --verbose

SPIRE_POD="spire-server-0"
SPIRE_CONTAINER="spire-server"
SPIRE_NAMESPACE="hpcs"
SPIRE_SOCKET="/tmp/spire-server/private/api.sock"
SPIRE_BIN="/opt/spire/bin/spire-server"
TRUST_DOMAIN="hpcs"

spire_exec() {
    kubectl exec -i "$SPIRE_POD" -c "$SPIRE_CONTAINER" -n "$SPIRE_NAMESPACE" -- \
        "$SPIRE_BIN" "$@" -socketPath "$SPIRE_SOCKET"
}

usage() {
    echo "Usage: $0 <agents|entries> [--all | --jq-selector <jq>] [--verbose]"
    exit 1
}

verb=""
all=false
jq_selector=""
verbose=false

while [ "$#" -gt 0 ]; do
    case "$1" in
        agents|entries)
            verb="$1"
            shift
            ;;
        --all)
            all=true
            shift
            ;;
        --jq-selector)
            jq_selector="$2"
            shift 2
            ;;
        --verbose)
            verbose=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

if [ -z "$verb" ]; then
    echo "Error: verb required (agents or entries)"
    usage
fi

if [ "$all" = false ] && [ -z "$jq_selector" ]; then
    echo "Error: specify --all or --jq-selector"
    usage
fi

if [ "$verb" = "agents" ]; then
    if [ -z "$jq_selector" ]; then
        jq_selector='.agents[].id.path'
    fi

    items=$(spire_exec agent list -output json | jq -r "$jq_selector" | tr -d ' \t')

    if [ -z "$items" ]; then
        echo "No agents matched."
        exit 0
    fi

    for agent_path in $items; do
        spiffe_id="spiffe://${TRUST_DOMAIN}${agent_path}"
        result=$(spire_exec agent evict -spiffeID "$spiffe_id" 2>&1)
        if [ $? -eq 0 ]; then
            [ "$verbose" = true ] && echo "Evicted agent: $spiffe_id"
        else
            echo "Failed to evict agent: $spiffe_id"
            [ "$verbose" = true ] && echo "$result"
        fi
    done

elif [ "$verb" = "entries" ]; then
    if [ -z "$jq_selector" ]; then
        jq_selector='.entries[].id'
    fi

    items=$(spire_exec entry show -output json | jq -r "$jq_selector" | tr -d ' \t')

    if [ -z "$items" ]; then
        echo "No entries matched."
        exit 0
    fi

    for entry_id in $items; do
        result=$(spire_exec entry delete -entryID "$entry_id" 2>&1)
        if [ $? -eq 0 ]; then
            [ "$verbose" = true ] && echo "Deleted entry: $entry_id"
        else
            echo "Failed to delete entry: $entry_id"
            [ "$verbose" = true ] && echo "$result"
        fi
    done
fi
