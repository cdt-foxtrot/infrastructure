# Cyber Defense Techniques - Foxtrot Infrastructure

## build.sh
This script sets up the Foxtrot Competition Infrastructure

It Creates:
1. Three private networks for the Blue, Red, and Gray Team
2. 4 Windows Server 2019 VMs (DC, IIS, Nginx, WinRM)
3. 7 Ubuntu VMs (SQL, Samba, NTP, Apache, Mail, ELK)
4. 10 Ubuntu VMs (Red Team)
5. 2 Gray Team Containers

## destroy.sh
This script destroys the Foxtrot Competition Infrastructure. This is primarily for testing purposes.

## services/
This directory contains all of the Ansible scripts to set up the 9 services:
1. Apache
2. Domain Controller/Active Directory/DNS
3. ELK
4. IIS
5. Mail Server
6. MySQL
7. NTP
8. OSSEC
9. Samba
10. WinRM

## inventory.ini
This file groups the IP addresses for the competition infrastructure in the following ways:

1. Blue Team Machines
2. Blue Team Windows Machines
3. Blue Team Linux Machines
4. Red Team Machines
5. Gray Team Machines
6. Individual Services (ex. Domain Controller, IIS Server, Mail Server, etc.)

## deploy.yml
This is the main Ansible Playbook that is called in the build.sh script. This imports all of the anisble playbooks for the infrastructure and sets up and install all of the services.
