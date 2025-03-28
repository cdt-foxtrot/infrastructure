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
# 1. Grayteam user on all Linux boxes (For Ansible)
# 2. Opens SSH Port on all Linux boxes (For Ansible)

# Declares the work and project environment
export ANSIBLE_INCUS_REMOTE=gcicompute02
export ANSIBLE_INCUS_PROJECT=cdtfoxtrot

# Gray Team
Admin1="Admin-1"
Admin2="Admin-2"
Admin3="Admin-3"

# Blue Team
DC="River"
IIS="Swamp"
Nginx="Beach"
WinRM="Ocean"
Apache="Plains"
SQL="Forest"
Mail="Savanna"
NTP="Taiga"
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

# Cleanup existing Greyteam users
cleanup_existing_users() {
    print_message "Starting cleanup of existing users..."
    
    # Cleanup Linux containers
    for linux_container in ${Admin1} ${Admin2} \
                        ${Nether1} ${Nether2} ${Nether3} ${Nether4} ${Nether5} \
                        ${Nether6} ${Nether7} ${Nether8} ${Nether9} ${Nether10} \
                        ${Apache} ${SQL} ${Mail} ${NTP} ${Samba} ${ELK}; do
        print_message "Cleaning Greyteam from ${linux_container}..."
        print_command "incus exec ${linux_container} -- bash -c 'sudo userdel -r Greyteam 2>/dev/null || true'"
        print_command "incus exec ${linux_container} -- bash -c 'sudo rm -rf /home/Greyteam 2>/dev/null || true'"
    done
}

# Creating Greyteam User on All Linux Boxes
add_greyteam_user() {
    local target=$1
    
    print_message "Adding Users to ${target}..."
    print_command "incus exec ${target} -- bash -c 'if ! id -u Greyteam >/dev/null 2>&1; then sudo useradd -m -s /bin/bash greyteam-1; else echo \"User already exists\"; fi'"
    print_command "incus exec ${target} -- bash -c 'echo \"Greyteam:SteveSexy!\" | sudo chpasswd'"
    print_command "incus exec ${target} -- bash -c 'sudo usermod -aG sudo Greyteam'"
    print_command "incus exec ${target} -- bash -c 'sudo mkdir -p /home/Greyteam/.ssh'"
    print_command "incus exec ${target} -- bash -c 'sudo chown -R Greyteam:Greyteam /home/Greyteam/.ssh'"
}

# Enable SSH on Linux containers
enable_ssh() {
    local target=$1
    
    print_message "Enabling SSH on ${target}..."
    # Install SSH server if not installed
    print_command "incus exec ${target} -- bash -c 'sudo apt-get update >/dev/null && sudo apt-get install -y openssh-server >/dev/null 2>&1 || true'"
    # Ensure SSH is running
    print_command "incus exec ${target} -- bash -c 'sudo systemctl enable ssh >/dev/null 2>&1 || true'"
    print_command "incus exec ${target} -- bash -c 'sudo systemctl start ssh >/dev/null 2>&1 || true'"
    # Open SSH port in firewall (assuming ufw is used)
    print_command "incus exec ${target} -- bash -c 'sudo ufw allow 22/tcp >/dev/null 2>&1 || true'"
}

# Main execution
cleanup_existing_users

# Add Greyteam User to all Linux containers
for linux_container in ${Admin1} ${Admin2} \
                      ${Nether1} ${Nether2} ${Nether3} ${Nether4} ${Nether5} \
                      ${Nether6} ${Nether7} ${Nether8} ${Nether9} ${Nether10} \
                      ${Apache} ${SQL} ${Mail} ${NTP} ${Samba} ${ELK}; do
    add_greyteam_user "${linux_container}"
    enable_ssh "${linux_container}"
done

print_message "Grayteam users added to all linux systems!"
print_message "SSH enabled on all linux systems!"
