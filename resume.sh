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
# This script resumes the Foxtrot Competition Infrastructure

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
print_command "incus resume ${DC} 2>/dev/null || true"
print_command "incus resume ${IIS} 2>/dev/null || true"
print_command "incus resume ${Nginx} 2>/dev/null || true"
print_command "incus resume ${WinRM} 2>/dev/null || true"
print_command "incus resume ${Apache} 2>/dev/null || true"
print_command "incus resume ${SQL} 2>/dev/null || true"
print_command "incus resume ${Mail} 2>/dev/null || true"
print_command "incus resume ${FTP} 2>/dev/null || true"
print_command "incus resume ${Samba} 2>/dev/null || true"
print_command "incus resume ${ELK} 2>/dev/null || true"
#print_command "incus resume ${Nether-1} 2>/dev/null || true"
#print_command "incus resume ${Nether-2} 2>/dev/null || true"
#print_command "incus resume ${Nether-3} 2>/dev/null || true"
#print_command "incus resume ${Nether-4} 2>/dev/null || true"
#print_command "incus resume ${Nether-5} 2>/dev/null || true"
#print_command "incus resume ${Nether-6} 2>/dev/null || true"
#print_command "incus resume ${Nether-7} 2>/dev/null || true"
#print_command "incus resume ${Nether-8} 2>/dev/null || true"
#print_command "incus resume ${Nether-9} 2>/dev/null || true"
#print_command "incus resume ${Nether-10} 2>/dev/null || true"
