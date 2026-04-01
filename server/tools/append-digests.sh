#!/bin/sh
#
# append-digests.sh — Append image digests for one or more Docker images to server/tools/digests.
#
# Usage:
#   append-digests.sh <image> [<image> ...]
#
# Examples:
#   append-digests.sh ghcr.io/cscfi/hpcs/data-prep:dev-20260323
#   append-digests.sh ghcr.io/cscfi/hpcs/data-prep:dev-20260323 \
#                     ghcr.io/cscfi/hpcs/container-prep:dev-20260323 \
#                     ghcr.io/cscfi/hpcs/job-prep:dev-20260323

DIGESTS_FILE="$(dirname "$0")/digests"

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <image> [<image> ...]"
    exit 1
fi

for image in "$@"; do
    digest=$(docker inspect "$image" --format='{{.Id}}' 2>&1)
    if [ $? -ne 0 ] || [ -z "$digest" ]; then
        echo "Failed to inspect image '$image': $digest"
        continue
    fi

    if grep -qF "$digest" "$DIGESTS_FILE"; then
        echo "Already present: $digest  ($image)"
    else
        echo "$digest" >> "$DIGESTS_FILE"
        echo "Appended:        $digest  ($image)"
    fi
done
