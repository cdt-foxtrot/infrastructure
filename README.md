# Cyber Defense Techniques - Foxtrot Infrastructure

## build.sh
This script sets up the Foxtrot Competition Infrastructure

It Creates:
1. Two private networks for the Blue and Red Team
2. 3 Windows Server 2019 VMs (DC, IIS/FTP, CA)
3. 7 Ubuntu VMs (SQL, Samba, OSSEC, NTP, Apache, Mail, Worker)
4. 10 Kali VMs (Red Team)
5. 1 Gray Team Container
6. 1 pfSense Router

## destroy.sh
This script destroys the Foxtrot Competition Infrastructure. This is primarily for testing purposes.

## services/
This directory contains all of the Ansible scripts to set up the 9 services:
1. Apache
2. Certificate Authority
3. Domain Controller/Active Directory/DNS
4. IIS
5. Mail Server
6. MySQL
7. NTP
8. OSSEC
9. Samba

## inventory.ini
This file groups the IP addresses for the competition infrastructure in the following ways:

1. Blue Team Machines
2. Blue Team Windows Machines
3. Blue Team Linux Machines
4. Red Team Machines
5. Individual Services (ex. Domain Controller, CA Server, Mail Server, etc.)

## site.yml
This is the main Ansible Playbook that is called in the build.sh script. This imports all of the anisble playbooks for the infrastructure and sets up and install all of the services.
