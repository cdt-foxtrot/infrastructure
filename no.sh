#!/bin/bash
set -euo pipefail

# Define networks
NETWORKS=("minecraft.net" "herobrine.net" "notch.net")

# Remove all network peerings first
for network in "${NETWORKS[@]}"; do
    if incus network show "$network" >/dev/null 2>&1; then
        echo "Removing peerings from $network..."
        # List and delete all peerings for this network
        incus network peer list "$network" | while read -r peer; do
            incus network peer delete "$network" "$peer"
        done
    fi
done

# Now force delete the networks
for network in "${NETWORKS[@]}"; do
    if incus network show "$network" >/dev/null 2>&1; then
        echo "Force deleting $network..."
        incus network delete "$network" --force
    fi
done

echo "All networks and peerings have been removed."
