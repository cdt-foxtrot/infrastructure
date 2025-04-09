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
print_message "Resuming existing resources..."
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
print_command "incus resume ${Nether1} 2>/dev/null || true"
print_command "incus resume ${Nether2} 2>/dev/null || true"
print_command "incus resume ${Nether3} 2>/dev/null || true"
print_command "incus resume ${Nether4} 2>/dev/null || true"
print_command "incus resume ${Nether5} 2>/dev/null || true"
print_command "incus resume ${Nether6} 2>/dev/null || true"
print_command "incus resume ${Nether7} 2>/dev/null || true"
print_command "incus resume ${Nether8} 2>/dev/null || true"
print_command "incus resume ${Nether9} 2>/dev/null || true"
print_command "incus resume ${Nether10} 2>/dev/null || true"
print_message "Resources resumed..."

print_message "Restarting spice connections..."
print_command "systemctl --user stop *${DC}*"
print_command "systemctl --user start *${DC}*"
print_command "systemctl --user stop *${IIS}*"
print_command "systemctl --user start *${IIS}*"
print_command "systemctl --user stop *${Nginx}*"
print_command "systemctl --user start *${Nginx}*"
print_command "systemctl --user stop *${WinRM}*"
print_command "systemctl --user start *${WinRM}*"
print_command "systemctl --user stop *${Apache}*"
print_command "systemctl --user start *${Apache}*"
print_command "systemctl --user stop *${SQL}*"
print_command "systemctl --user start *${SQL}*"
print_command "systemctl --user stop *${Mail}*"
print_command "systemctl --user start *${Mail}*"
print_command "systemctl --user stop *${FTP}*"
print_command "systemctl --user start *${FTP}*"
print_command "systemctl --user stop *${Samba}*"
print_command "systemctl --user start *${Samba}*"
print_command "systemctl --user stop *${ELK}*"
print_command "systemctl --user start *${ELK}*"
print_command "systemctl --user stop *${Nether1}*"
print_command "systemctl --user start *${Nether1}*"
print_command "systemctl --user stop *${Nether2}*"
print_command "systemctl --user start *${Nether2}*"
print_command "systemctl --user stop *${Nether3}*"
print_command "systemctl --user start *${Nether3}*"
print_command "systemctl --user stop *${Nether4}*"
print_command "systemctl --user start *${Nether4}*"
print_command "systemctl --user stop *${Nether5}*"
print_command "systemctl --user start *${Nether5}*"
print_command "systemctl --user stop *${Nether6}*"
print_command "systemctl --user start *${Nether6}*"
print_command "systemctl --user stop *${Nether7}*"
print_command "systemctl --user start *${Nether7}*"
print_command "systemctl --user stop *${Nether8}*"
print_command "systemctl --user start *${Nether8}*"
print_command "systemctl --user stop *${Nether9}*"
print_command "systemctl --user start *${Nether9}*"
print_command "systemctl --user stop *${Nether10}*"
print_command "systemctl --user start *${Nether10}*"
