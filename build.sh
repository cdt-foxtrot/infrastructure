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
# 1. Three private networks for the Gray, Blue, and Red Team
# 2. 4 Windows Server 2019 VMs (DC, IIS, Nginx, WinRM)
# 3. 6 Ubuntu VMs (SQL, Samba, FTP, Apache, Mail, ELK)
# 4. 10 Ubuntu Containers (Red Team)
# 5. 4 Gray Team Containers

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
Admin3="Admin-3"
Admin3_IP="10.10.1.3"
Admin4="Admin-4"
Admin4_IP="10.10.1.4"

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
FTP="Taiga"
Samba="Jungle"
ELK="Desert"
Apache_IP="10.150.1.5"
SQL_IP="10.150.1.6"
Mail_IP="10.150.1.7"
FTP_IP="10.150.1.8"
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
print_command "incus stop --force ${FTP} 2>/dev/null || true"
print_command "incus delete ${FTP} 2>/dev/null || true"
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
print_command "incus stop --force ${Admin3} 2>/dev/null || true"
print_command "incus delete ${Admin3} 2>/dev/null || true"
print_command "incus stop --force ${Admin4} 2>/dev/null || true"
print_command "incus delete ${Admin4} 2>/dev/null || true"

# Deleting Networks
delete_peering() {
    local network=$1
    local peering_name=$2
    if incus network show "$network" >/dev/null 2>&1; then
        if incus network peer list "$network" | grep -q "$peering_name"; then
            print_command "incus network peer delete \"$network\" \"$peering_name\""
        else
            echo "Peering $peering_name not found on $network (skipping)"
        fi
    else
        echo "Network $network not found (skipping peering deletion)"
    fi
}

# Delete peerings (with existence checks)
print_message "Deleting network peerings..."
delete_peering "$BLUE_NETWORK" "blue-to-red"
delete_peering "$BLUE_NETWORK" "blue-to-gray"
delete_peering "$RED_NETWORK" "red-to-blue"
delete_peering "$RED_NETWORK" "red-to-gray"
delete_peering "$GRAY_NETWORK" "gray-to-blue"
delete_peering "$GRAY_NETWORK" "gray-to-red"

# Delete networks (with force and error suppression)
print_message "Deleting networks..."
for network in "$GRAY_NETWORK" "$BLUE_NETWORK" "$RED_NETWORK"; do
    if incus network show "$network" >/dev/null 2>&1; then
        print_command "incus network delete \"$network\" 2>/dev/null || true"
    else
        echo "Network $network not found (skipping deletion)"
    fi
done

# Creates a private network for the Gray Team VMs
print_message "Creating Gray Team Network..."
print_command "incus network create ${GRAY_NETWORK} \\
ipv4.address=10.10.1.100/24 \\
ipv4.nat=true \\
ipv6.address=none \\
ipv6.nat=false"

# Creates a private network for the Blue Team VMs
print_message "Creating Blue Team Network..."
print_command "incus network create ${BLUE_NETWORK} \\
ipv4.address=10.150.1.100/24 \\
ipv4.nat=true \\
ipv6.address=none \\
ipv6.nat=false"

# Creates a private network for the Red Team VMs
print_message "Creating Red Team Network..."
print_command "incus network create ${RED_NETWORK} \\
ipv4.address=10.0.10.100/24 \\
ipv4.nat=true \\
ipv6.address=none \\
ipv6.nat=false"

# Connecting Networks with bidirectional peering
print_message "Setting up network peering..."

# Blue ↔ Red peering
print_command "incus network peer create ${BLUE_NETWORK} blue-to-red ${RED_NETWORK}"
print_command "incus network peer create ${RED_NETWORK} red-to-blue ${BLUE_NETWORK}"

# Blue ↔ Gray peering
print_command "incus network peer create ${BLUE_NETWORK} blue-to-gray ${GRAY_NETWORK}"
print_command "incus network peer create ${GRAY_NETWORK} gray-to-blue ${BLUE_NETWORK}"

# Red ↔ Gray peering
print_command "incus network peer create ${RED_NETWORK} red-to-gray ${GRAY_NETWORK}"
print_command "incus network peer create ${GRAY_NETWORK} gray-to-red ${RED_NETWORK}"

# Creates Admin1 (Gray) Container
print_message "Creating Admin1 Container..."
print_command "incus launch images:ubuntu/noble ${Admin1} \\
--network \"${GRAY_NETWORK}\" \\
--device \"eth0,ipv4.address=${Admin1_IP}\" -t c4-m8"

# Creates Admin2 (Gray) Ubuntu VM
print_message "Creating Admin2 VM..."
print_command "incus launch images:ubuntu/noble/desktop ${Admin2} \\
--vm \\
--network \"${GRAY_NETWORK}\" \\
--device \"eth0,ipv4.address=${Admin2_IP}\" -t c4-m8"

# Creates Admin3 (Gray) Ubuntu VM
print_message "Creating Admin3 VM..."
print_command "incus launch images:ubuntu/noble/desktop ${Admin3} \\
--vm \\
--network \"${GRAY_NETWORK}\" \\
--device \"eth0,ipv4.address=${Admin3_IP}\" -t c4-m8"

# Creates Admin4 (Gray) Windows VM
print_message "Creating Admin4 VM..."
print_command "incus launch oszoo:winsrv/2019/ansible-cloud \\
${Admin4} \\
--vm \\
--config limits.cpu=8 \\
--config limits.memory=16GiB \\
--network \"${GRAY_NETWORK}\" \\
--device \"eth0,ipv4.address=${Admin4_IP}\" \\
--device \"root,size=320GiB\""

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

# Creates Windows IIS VM
print_message "Creating IIS VM..."
print_command "incus launch oszoo:winsrv/2019/ansible-cloud \\
${IIS} \\
--vm \\
--config limits.cpu=8 \\
--config limits.memory=16GiB \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${IIS_IP}\" \\
--device \"root,size=320GiB\""

# Creates Windows Nginx VM
print_message "Creating Nginx VM..."
print_command "incus launch oszoo:winsrv/2019/ansible-cloud \\
${Nginx} \\
--vm \\
--config limits.cpu=8 \\
--config limits.memory=16GiB \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nginx_IP}\" \\
--device \"root,size=320GiB\""

# Creates Windows WinRM VM
print_message "Creating WinRM VM..."
print_command "incus launch oszoo:winsrv/2019/ansible-cloud \\
${WinRM} \\
--vm \\
--config limits.cpu=8 \\
--config limits.memory=16GiB \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${WinRM_IP}\" \\
--device \"root,size=320GiB\""

# Open VGA consoles for Windows VMs in background
print_message "Launching Windows VMs"
print_command "incus console --type=vga ${DC} &"
print_command "incus console --type=vga ${IIS} &"
print_command "incus console --type=vga ${Nginx} &"
print_command "incus console --type=vga ${WinRM} &"
print_command "incus console --type=vga ${Admin-4} &"

# Creates Ubuntu Apache VM
print_message "Creating Apache VM..."
print_command "incus launch images:ubuntu/noble/desktop ${Apache} \\
--vm
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${Apache_IP}\" -t c4-m8"

# Creates Ubuntu SQL VM
print_message "Creating SQL VM..."
print_command "incus launch images:ubuntu/noble/desktop ${SQL} \\
--vm
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${SQL_IP}\" -t c4-m8"

# Creates Ubuntu Mail VM
print_message "Creating Mail VM..."
print_command "incus launch images:ubuntu/noble/desktop ${Mail} \\
--vm
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${Mail_IP}\" -t c4-m8"

# Creates Ubuntu FTP VM
print_message "Creating FTP Container..."
print_command "incus launch images:ubuntu/noble/desktop ${FTP} \\
--vm \\
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${FTP_IP}\" -t c4-m8"

# Creates Ubuntu Samba VM
print_message "Creating Samba VM..."
print_command "incus launch images:ubuntu/noble/desktop ${Samba} \\
--vm
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${Samba_IP}\" -t c4-m8"

# Creates Ubuntu ELK VM
print_message "Creating ELK VM..."
print_command "incus launch images:ubuntu/noble/desktop ${ELK} \\
--vm
--network \"${BLUE_NETWORK}\" \\
--device \"eth0,ipv4.address=${ELK_IP}\" -t c4-m8"

# Creates Red Team Containers
print_message "Creating Red Team VM (1)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether1} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether1_IP}\" -t c4-m8"

print_message "Creating Red Team VM (2)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether2} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether2_IP}\" -t c4-m8"

print_message "Creating Red Team VM (3)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether3} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether3_IP}\" -t c4-m8"

print_message "Creating Red Team VM (4)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether4} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether4_IP}\" -t c4-m8"

print_message "Creating Red Team VM (5)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether5} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether5_IP}\" -t c4-m8"

print_message "Creating Red Team VM (6)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether6} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether6_IP}\" -t c4-m8"

print_message "Creating Red Team VM (7)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether7} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether7_IP}\" -t c4-m8"

print_message "Creating Red Team VM (8)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether8} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether8_IP}\" -t c4-m8"

print_message "Creating Red Team VM (9)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether9} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether9_IP}\" -t c4-m8"

print_message "Creating Red Team VM (10)..."
print_command "incus launch images:ubuntu/noble/desktop ${Nether10} \\
--vm \\
--network \"${RED_NETWORK}\" \\
--device \"eth0,ipv4.address=${Nether10_IP}\" -t c4-m8"

# Checks State of Windows VMs
print_message "Waiting for Windows VMs with progressive checks..."

# Improved check function
check_windows_vm() {
    local vm=$1
    local attempts=3
    local delay=5
    
    for ((i=1; i<=attempts; i++)); do
        if timeout 10 incus exec "$vm" -- cmd /c "echo Ready" 2>/dev/null; then
            return 0
        fi
        sleep $delay
    done
    return 1
}

total_wait=0
max_wait=900  # 15 minutes maximum
interval=30   # Check every 30 seconds

while [ $total_wait -lt $max_wait ]; do
    all_ready=true
    
    for windows_vm in ${DC} ${IIS} ${Nginx} ${WinRM}; do
        if ! check_windows_vm "$windows_vm"; then
            all_ready=false
            break
        fi
    done
    
    if $all_ready; then
        print_message "All Windows VMs ready after ${total_wait} seconds!"
        break
    fi
    
    print_message "Waiting ${interval} more seconds (${total_wait}/${max_wait})..."
    sleep $interval
    total_wait=$((total_wait + interval))
done
