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
# This script sets up the Foxtrot Competition Infrastructure
# It Creates:
# 1. Two private networks for the Blue and Red Team
# 2. 3 Windows Server 2019 VMs (DC, IIS/FTP, CA)
# 3. 7 Ubuntu VMs (SQL, Samba, OSSEC, NTP, Apache, Mail, Worker)
# 4. 1 pfSense Router
# 5. 10 Kali VMs (Red Team)
# 6. 1 Gray Team Container

# Sets Gray Team Information
GRAY_TEAM="foxtrot-grayteam"
GRAY_TEAM_IP="10.150.1.100"

# Declares the work and project environment
export ANSIBLE_INCUS_REMOTE=gcicompute02
export ANSIBLE_INCUS_PROJECT=cdtfoxtrot

# Networks
BLUE_NETWORK="minecraft.net"
RED_NETWORK="herobrine.net"

# Blue Team Windows
DC="River"
CA="Ocean"
IIS="Swamp"
DC_IP="10.150.1.10"
CA_IP="10.150.1.11"
IIS_IP="10.150.1.12"

# Blue Team Linux
Apache="Plains"
SQL="Forest"
Mail="Savanna"
NTP="Taiga"
Samba="Jungle"
OSSEC="Beach"
Worker="Desert"
Router="The-End"
Apache_IP="10.150.1.13"
SQL_IP="10.150.1.14"
Mail_IP="10.150.1.15"
NTP_IP="10.150.1.16"
Samba_IP="10.150.1.17"
OSSEC_IP="10.150.1.18"
Worker_IP="10.150.1.19"
Router_IP="10.150.1.254"

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
Nether1_IP="10.0.10.10"
Nether2_IP="10.0.10.11"
Nether3_IP="10.0.10.12"
Nether4_IP="10.0.10.13"
Nether5_IP="10.0.10.14"
Nether6_IP="10.0.10.15"
Nether7_IP="10.0.10.16"
Nether8_IP="10.0.10.17"
Nether9_IP="10.0.10.18"
Nether10_IP="10.0.10.19"

# Switches to correct Incus remote and project
print_command "incus remote switch gcicompute02"
print_command "incus project switch cdtfoxtrot"

# Cleanup existing resources
print_message "Cleaning up existing resources..."
print_command "incus stop --force ${DC} 2>/dev/null || true"
print_command "incus delete ${DC} 2>/dev/null || true"
print_command "incus stop --force ${CA} 2>/dev/null || true"
print_command "incus delete ${CA} 2>/dev/null || true"
print_command "incus stop --force ${IIS} 2>/dev/null || true"
print_command "incus delete ${IIS} 2>/dev/null || true"
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
print_command "incus stop --force ${OSSEC} 2>/dev/null || true"
print_command "incus delete ${OSSEC} 2>/dev/null || true"
print_command "incus stop --force ${Worker} 2>/dev/null || true"
print_command "incus delete ${Worker} 2>/dev/null || true"
print_command "incus stop --force ${Router} 2>/dev/null || true"
print_command "incus delete ${Router} 2>/dev/null || true"
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
print_command "incus stop --force ${GRAY_TEAM} 2>/dev/null || true"
print_command "incus delete ${GRAY_TEAM} 2>/dev/null || true"
print_command "incus network delete ${BLUE_NETWORK} 2>/dev/null || true"
print_command "incus network delete ${RED_NETWORK} 2>/dev/null || true"

# Creates a private network for the Blue Team VMs
print_message "Creating Blue Team Network..."
print_command "incus network create ${BLUE_NETWORK} \\
ipv4.address=10.150.1.1/24 \\
ipv4.nat=true \\
ipv6.address=none \\
ipv6.nat=false"

# Creates a private network for the Red Team VMs
print_message "Creating Red Team Network..."
print_command "incus network create ${RED_NETWORK} \\
ipv4.address=10.0.10.1/24 \\
ipv4.nat=true \\
ipv6.address=none \\
ipv6.nat=false"

# Creates Gray Team Container
print_message "Creating Gray Team Container..."
print_command "incus launch images:ubuntu/noble ${GRAY_TEAM} \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${GRAY_TEAM_IP}\" -t c4-m8"

# Creates Windows DC VM
print_message "Creating DC VM..."
print_command "incus launch oszoo:winsrv/2019/ansible-cloud \\
${DC} \\
--vm \\
--config limits.cpu=8 \\
--config limits.memory=16GiB \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${DC_IP}\" \\
--device \"root,size=320GiB\""

# Creates Red Team Container
print_message "Creating Red Team Container (1)..."
print_command "incus launch images:kali ${Nether1} \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether1_IP}\" -t c4-m8"
