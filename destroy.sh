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
# This script destroys the Foxtrot Competition Infrastructure
# This is primarly for testing purposes

# Declares the work and project environment
export ANSIBLE_INCUS_REMOTE=gcicompute02
export ANSIBLE_INCUS_PROJECT=cdtfoxtrot

# Networks
BLUE_NETWORK="minecraft.net"
RED_NETWORK="herobrine.net"
GRAY_NETWORK="notch.net"

# Gray Team
Admin1="Admin-1"
Admin1_IP="10.10.1.1"
Admin2="Admin-2"
Admin2_IP="10.10.1.2"

# Blue Team Windows
DC="River"
IIS="Swamp"
Nginx="Beach"
WinRM="Ocean"
DC_IP="10.150.1.1"
IIS_IP="10.150.1.2"
Nginx_IP="10.150.1.3"
WinRM_IP="10.150.1.4"

# Blue Team Linux
Apache="Plains"
SQL="Forest"
Mail="Savanna"
NTP="Taiga"
Samba="Jungle"
ELK="Desert"
Apache_IP="10.150.1.5"
SQL_IP="10.150.1.6"
Mail_IP="10.150.1.7"
NTP_IP="10.150.1.8"
Samba_IP="10.150.1.9"
ELK_IP="10.150.1.10"

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
Nether1_IP="10.0.10.1"
Nether2_IP="10.0.10.2"
Nether3_IP="10.0.10.3"
Nether4_IP="10.0.10.4"
Nether5_IP="10.0.10.5"
Nether6_IP="10.0.10.6"
Nether7_IP="10.0.10.7"
Nether8_IP="10.0.10.8"
Nether9_IP="10.0.10.9"
Nether10_IP="10.0.10.10"

# Switches to correct Incus remote and project
print_command "incus remote switch gcicompute02"
print_command "incus project switch cdtfoxtrot"

# Cleanup existing resources
print_message "Cleaning up existing resources..."
print_command "incus stop --force ${DC} 2>/dev/null || true"
print_command "incus delete ${DC} 2>/dev/null || true"
print_command "incus stop --force ${IIS} 2>/dev/null || true"
print_command "incus delete ${IIS} 2>/dev/null || true"
print_command "incus stop --force ${Nginx} 2>/dev/null || true"
print_command "incus delete ${Nginx} 2>/dev/null || true"
print_command "incus stop --force ${WinRM} 2>/dev/null || true"
print_command "incus delete ${WinRM} 2>/dev/null || true"
print_command "incus stop --force ${Apache} 2>/dev/null || true"
print_command "incus delete ${Apache} 2>/dev/null || true"
print_command "incus stop --force ${SQL} 2>/dev/null || true"
print_command "incus delete ${SQL} 2>/dev/null || true"
print_command "incus stop --force ${Mail} 2>/dev/null || true"
print_command "incus delete ${Mail} 2>/dev/null || true"
print_command "incus stop --force ${NTP} 2>/dev/null || true"
print_command "incus delete ${NTP} 2>/dev/null || true"
print_command "incus stop --force ${Samba} 2>/dev/null || true"
print_command "incus delete ${Samba} 2>/dev/null || true"
print_command "incus stop --force ${ELK} 2>/dev/null || true"
print_command "incus delete ${ELK} 2>/dev/null || true"
print_command "incus stop --force ${Nether1} 2>/dev/null || true"
print_command "incus delete ${Nether1} 2>/dev/null || true"
print_command "incus stop --force ${Nether2} 2>/dev/null || true"
print_command "incus delete ${Nether2} 2>/dev/null || true"
print_command "incus stop --force ${Nether3} 2>/dev/null || true"
print_command "incus delete ${Nether3} 2>/dev/null || true"
print_command "incus stop --force ${Nether4} 2>/dev/null || true"
print_command "incus delete ${Nether4} 2>/dev/null || true"
print_command "incus stop --force ${Nether5} 2>/dev/null || true"
print_command "incus delete ${Nether5} 2>/dev/null || true"
print_command "incus stop --force ${Nether6} 2>/dev/null || true"
print_command "incus delete ${Nether6} 2>/dev/null || true"
print_command "incus stop --force ${Nether7} 2>/dev/null || true"
print_command "incus delete ${Nether7} 2>/dev/null || true"
print_command "incus stop --force ${Nether8} 2>/dev/null || true"
print_command "incus delete ${Nether8} 2>/dev/null || true"
print_command "incus stop --force ${Nether9} 2>/dev/null || true"
print_command "incus delete ${Nether9} 2>/dev/null || true"
print_command "incus stop --force ${Nether10} 2>/dev/null || true"
print_command "incus delete ${Nether10} 2>/dev/null || true"
print_command "incus stop --force ${Admin1} 2>/dev/null || true"
print_command "incus delete ${Admin1} 2>/dev/null || true"
print_command "incus stop --force ${Admin2} 2>/dev/null || true"
print_command "incus delete ${Admin2} 2>/dev/null || true"
print_command "incus network delete ${BLUE_NETWORK} 2>/dev/null || true"
print_command "incus network delete ${RED_NETWORK} 2>/dev/null || true"
print_command "incus network delete ${GRAY_NETWORK} 2>/dev/null || true"
