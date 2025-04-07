#!/bin/bash

set -euo pipefail

print_command() {
	echo "$(tput setaf 6)>>> $1$(tput sgr0)"
	eval "$1"
}

print_message() {
	echo "$(tput setaf 2)$1$(tput sgr0)"
}

# SCRIPT OVERVIEW:
# This script pauses the Foxtrot Competition Infrastructure

# Declares the work and project environment
export ANSIBLE_INCUS_REMOTE=gcicompute02
export ANSIBLE_INCUS_PROJECT=cdtfoxtrot

# Networks
BLUE_NETWORK="minecraft.net"
RED_NETWORK="herobrine.net"
GRAY_NETWORK="notch.net"

# Blue Team Windows
DC="River"
IIS="Swamp"
Nginx="Beach"
WinRM="Ocean"

# Blue Team Linux
Apache="Plains"
SQL="Forest"
Mail="Savanna"
FTP="Taiga"
Samba="Jungle"
ELK="Desert"

# Red Team
Nether1="Nether-1"
Nether2="Nether-2"
Nether3="Nether-3"
Nether4="Nether-4"
Nether5="Nether-5"
Nether6="Nether-6"
Nether7="Nether-7"
Nether8="Nether-8"
Nether9="Nether-9"
Nether10="Nether-10"

# Switches to correct Incus remote and project
print_command "incus remote switch gcicompute02"
print_command "incus project switch cdtfoxtrot"

# Pauses all instances
print_message "Pausing existing resources..."
print_command "incus pause --force ${DC} 2>/dev/null || true"
print_command "incus pause --force ${IIS} 2>/dev/null || true"
print_command "incus pause --force ${Nginx} 2>/dev/null || true"
print_command "incus pause --force ${WinRM} 2>/dev/null || true"
print_command "incus pause --force ${Apache} 2>/dev/null || true"
print_command "incus pause --force ${SQL} 2>/dev/null || true"
print_command "incus pause --force ${Mail} 2>/dev/null || true"
print_command "incus pause --force ${FTP} 2>/dev/null || true"
print_command "incus pause --force ${Samba} 2>/dev/null || true"
print_command "incus pause --force ${ELK} 2>/dev/null || true"
print_command "incus pause --force ${Nether-1} 2>/dev/null || true"
print_command "incus pause --force ${Nether-2} 2>/dev/null || true"
print_command "incus pause --force ${Nether-3} 2>/dev/null || true"
print_command "incus pause --force ${Nether-4} 2>/dev/null || true"
print_command "incus pause --force ${Nether-5} 2>/dev/null || true"
print_command "incus pause --force ${Nether-6} 2>/dev/null || true"
print_command "incus pause --force ${Nether-7} 2>/dev/null || true"
print_command "incus pause --force ${Nether-8} 2>/dev/null || true"
print_command "incus pause --force ${Nether-9} 2>/dev/null || true"
print_command "incus pause --force ${Nether-10} 2>/dev/null || true"
