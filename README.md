# dot1xConfig
This script is to aumatically check for devices being reachable on SSH and SNMPv3

## Logic
SSH Test on TCP Port 22
 
if SSH Test successful:
  SNMPv3 Test using all the users/passwords until one is correct
 
  if SNMPv3 Test successful:
    Save wich user is the correct one and change on TSNA/CSPC
    Append to a CSV file: deviceIP, SSH OK, SNMPv3 corrcet User/Password
 
  if SNMPv3 Test not successful:
    Send show snmp user/group/comunity
    Append to a CSV file: deviceIP, SSH OK, all incorrect user/passwords used
    Create .txt file for this device with show command outputs
 
if SSH Test not successful:
  ping the devices' IP address
 
  if Ping Test successful:
    SNMPv3 Test using all the users/passwords until one is correct
 
  if SNMPv3 Test successful:
    Save wich user is the correct one and change on TSNA/CSPC
    Append to a CSV file: deviceIP, SSH Not OK, SNMPv3 corrcet User/Password
 
  if SNMPv3 Test not successful:
    Send show snmp user/group/comunity
    Append to a CSV file: deviceIP, SSH Not OK, all incorrect user/passwords used
    Create .txt file for this device with show command outputs
    Add the device to a separate list (check SSH2 credentials list)
  if Ping Test not successful:
    discard device, add to NDLM decommision list