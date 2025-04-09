#!/bin/bash

set -euo pipefail

print_command() {
    echo "$(tput setaf 6)>>> $1$(tput sgr0)"
    eval "$1"
}

print_message() {
    echo "$(tput setaf 2)$1$(tput sgr0)"
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    print_message "Usage: $0 <box_name> [--restart]"
    print_message "  --restart: Include the incus restart command (disabled by default)"
    exit 1
fi

# Get the box name from the first argument
BOX="$1"
shift

# Default to NOT performing restart
DO_RESTART=false

# Process remaining arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --restart)
            DO_RESTART=true
            ;;
        *)
            print_message "Unknown option: $1"
            print_message "Usage: $0 <box_name> [--restart]"
            exit 1
            ;;
    esac
    shift
done

print_message "Processing box: $BOX"

print_message "Stopping spice for $BOX..."
print_command "systemctl --user stop *${BOX}*"

if [ "$DO_RESTART" = true ]; then
    print_message "Restarting incus container $BOX..."
    print_command "incus restart ${BOX} --force"
fi

print_message "Starting spice for $BOX..."
print_command "systemctl --user start *${BOX}*"

print_message "Refreshed $BOX"
