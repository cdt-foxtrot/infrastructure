# Cyber Defense Techniques - Foxtrot Infrastructure

## SETUP INSTRUCTIONS
1. run build.sh
2. console into the windows boxes
3. set windows password to admin:
   - wget -o winsetup.ps1 https://raw.githubusercontent.com/cdt-foxtrot/infrastructure/refs/heads/main/winsetup.ps1
7. run linuxsetup.sh script
8. on an admin machine (admin1):
   - install ansible
   - install git
   - install sshpass
6. git clone the repo
7. ansible-playbook -i inventory.ini winusers/winusers.yml
8. ansible-playbook -i inventory.ini linuxusers.yml
9. ansible-playbook -i inventory.ini deploy.yml
10. Manually go into Beach (Nginx) and start the service:
    - cd C:\nginx\nginx-1.24.0
    - start nginx

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
