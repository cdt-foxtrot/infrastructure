# Set user details
$Username = "Greyteam"
$Password = ConvertTo-SecureString "SteveSexy!" -AsPlainText -Force

# Create the user
New-LocalUser -Name $Username -Password $Password -FullName "Greyteam" -Description "Greyteam User DO NOT DELETE"

# Add the user to Administrators group
Add-LocalGroupMember -Group "Administrators" -Member $Username

# Enable WinRM service
Set-Service -Name WinRM -StartupType Automatic
Start-Service -Name WinRM

# Enable PowerShell Remoting
Enable-PSRemoting -Force

# Turns of Firewall and Windows Defender
Set-NetFirewallProfile -All -Enabled False
Set-MpPreference -DisableRealtimeMonitoring $true
Set-MpPreference -MAPSReporting 0
Set-MpPreference -SubmitSamplesConsent 2

# Allow WinRM through firewall
New-NetFirewallRule -DisplayName "Allow WinRM" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow

# Enable ICMP (Ping)
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -Direction Inbound -Action Allow
New-NetFirewallRule -DisplayName "Allow ICMPv6-In" -Protocol ICMPv6 -Direction Inbound -Action Allow

# Turns off NLA
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v SecurityLayer /t REG_DWORD /d 0 /f | Out-Null

Write-Host "User 'Greyteam' created, added to Administrators, WinRM enabled, and ICMP allowed." -ForegroundColor Green
