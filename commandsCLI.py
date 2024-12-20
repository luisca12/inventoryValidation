from functions import checkConnect22, logInCSV, genTxtFile, pingDevice
from netmiko import ConnectHandler
from snmpWalk import snmpWalkv3
from log import authLog

import traceback
import threading
import asyncio
import time
import os

shHostname = "show run | i hostname"
shSNMP = [
    'do show snmp user',
    'do show snmp group'
]


def testInven(validIPs, username, netDevice):
    # This function is to take a show run

    validIPs = [validIPs]
    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"Connecting to device {validDeviceIP}...")
            authLog.info(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                authLog.info(f"Connected to device {validDeviceIP}...")

                sshAccess.enable()
                authLog.info(f"Automation successfully run the command enable")
                shHostnameOut = sshAccess.send_command(shHostname)
                authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                shHostnameOut = shHostnameOut.split(' ')[1]
                shHostnameOut = shHostnameOut + "#"

                if checkConnect22(validDeviceIP):
                    authLog.info(f"Device IP {validDeviceIP} is reachable on Port TCP 22.")
                    print(f"INFO: Device IP {validDeviceIP} is reachable on Port TCP 22.")
                    snmpv3User, snmpCredentials = asyncio.run(snmpWalkv3(validDeviceIP, username))

                    if snmpv3User and snmpCredentials:
                        authLog.info(f"Device: {validDeviceIP}, succesfilly passed SSH and SNMPv3 checks with SNMPv3 User: {snmpv3User}")
                        logInCSV(validDeviceIP, "Devices totally reachable", "SSH OK", "SNMPv3 OK", f"SNMPv3 User: {snmpv3User}")
                        print(f"Device: {validDeviceIP}, succesfilly passed SSH and SNMPv3 checks with SNMPv3 User: {snmpv3User}")
                        continue
                    else:
                        shSNMPout = sshAccess.send_config_set(shSNMP)
                        authLog.info(f"Automation successfully ran the below commands:\n{shHostnameOut}\n{shSNMPout}")
                        print(f"INFO: Automation successfully ran the below commands:\n{shHostnameOut}\n{shSNMPout}")
                        logInCSV(validDeviceIP, "Devices with SSH but SNMPv3 wrong", "SSH OK", "SNMPv3 not OK")
                        genTxtFile(validDeviceIP, username,"SNMPv3 Outputs", snmpCredentials, shSNMPout)
                        continue
                else:
                    authLog.info(f"Device IP {validDeviceIP} is not reachable on Port TCP 22.")
                    print(f"INFO: Device IP {validDeviceIP} is not reachable on Port TCP 22.")
            
        except Exception as error:
            print(f"ERROR: SSH to device {validDeviceIP} failed")
            authLog.error(f"SSH to device {validDeviceIP} failed")
            pingOut = pingDevice(validDeviceIP)

            if pingOut:
                snmpv3User, snmpCredentials = asyncio.run(snmpWalkv3(validDeviceIP, username))
                if snmpv3User and snmpCredentials:
                    authLog.info(f"Device: {validDeviceIP}, succesfully passed ping and SNMPv3, SSH not OK, SNMPv3 OK, SNMPv3 User: {snmpv3User}")
                    logInCSV(validDeviceIP, "Devices wihtout SSH but ping reachable and SNMP OK", "SSH not OK","Ping OK", f"SNMPv3 User: {snmpv3User}")
                    print(f"Device: {validDeviceIP}, succesfully passed ping and SNMPv3, SSH not OK, SNMPv3 OK, SNMPv3 User: {snmpv3User}")
                else:
                    logInCSV(validDeviceIP, "Devices without SSH, SNMPv3 but ping OK", "SSH not OK", "SNMPv3 not OK", "Ping OK")
            else:
                print(f"INFO: Device {validDeviceIP} Totally not reachable.")
                authLog.info(f"Device {validDeviceIP} Totally not reachable.")
                logInCSV(validDeviceIP, "Devices Totally not reachable", "SSH not OK", "SNMPv3 not OK", "Ping not OK")

            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.error(traceback.format_exc())
            with open(f"Devices that failed to apply config.txt","a") as failedDevices:
                failedDevices.write(f"User {username} connected to {validDeviceIP} got an error: {error}\n")      

def testInvenThread(validIPs, username, netDevice):
    threads = []

    for validDeviceIP in validIPs:
        thread = threading.Thread(target=testInven, args=(validDeviceIP, username, netDevice))
        thread.start()
        authLog.info(f"Thread {thread} started.")
        threads.append(thread)
        authLog.info(f"Thread {thread} appended to threads: {threads}")

    for thread in threads:
        thread.join()