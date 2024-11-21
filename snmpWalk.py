"""
SNMPv3: auth SHA, privacy AES128
++++++++++++++++++++++++++++++++
Send SNMP GET request using the following options:
* with SNMPv3, user 'usr-sha-aes', SHA authentication, AES128 encryption
* over IPv4/UDP
* to an Agent at demo.pysnmp.com:161
* for SNMPv2-MIB::sysDescr.0 MIB object
Available authentication protocols:
#. usmHMACMD5AuthProtocol
#. usmHMACSHAAuthProtocol
#. usmHMAC128SHA224AuthProtocol
#. usmHMAC192SHA256AuthProtocol
#. usmHMAC256SHA384AuthProtocol
#. usmHMAC384SHA512AuthProtocol
#. usmNoAuthProtocol
Available privacy protocols:
#. usmDESPrivProtocol
#. usm3DESEDEPrivProtocol
#. usmAesCfb128Protocol
#. usmAesCfb192Protocol
#. usmAesCfb256Protocol
#. usmNoPrivProtocol
Functionally similar to:
| $ snmpget -v3 -l authPriv -u usr-sha-aes -A authkey1 -X privkey1 -a SHA -x AES demo.pysnmp.com SNMPv2-MIB::sysDescr.0
"""  #
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.hlapi import *
from log import authLog
import traceback
import os

# 1.3.6.1.2.1.4.28.1 # 1.3.6.1.2.1.1
async def snmpWalkv3(validDeviceIP, username):
    """
    Perform an SNMPv3 walk.

    :param validDeviceIP: The SNMP device IP or hostname.
    :return: user, snmpCredentials
    """
    oid="1.3.6.1.2.1.1.3"
    
    snmpCredentials = {
        'user1': ['authPass1','privPass1123'],
        'user2': ['authPass2','privPass2123'],
        'user3': ['authPass3','privPass3123']
    }

    try:
        for user in snmpCredentials.keys():
            print(f"INFO: Testing SNMPv3 with user: {user} on device: {validDeviceIP}")
            authLog.info(f"Testing SNMPv3 with user: {user} on device: {validDeviceIP}")
            
            authPass = snmpCredentials[user][0]
            privPass = snmpCredentials[user][1]
        
            # Create the SNMPv3 context
            iterator = await next_cmd(
                SnmpEngine(),
                UsmUserData(
                    user, 
                    authKey=authPass, 
                    privKey=privPass, 
                    authProtocol=usmHMACSHAAuthProtocol, 
                    privProtocol=usmAesCfb128Protocol),
                await UdpTransportTarget.create((validDeviceIP, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            authLog.info(f"Iterator created for user: {user} on device: {validDeviceIP}, iterator: {iterator}")

            errorIndication, errorStatus, errorIndex, varBinds = iterator

            if errorIndication:
                authLog.error(f"Device: {validDeviceIP} got an error tesing SNMPv3 user: {user}, error: {errorIndication}")
                authLog.error(f"Possible errors: User not found, Wrong SNMP PDU digest (wrong Auth password), No SNMP response received before timeout (Wrong priv password)")
                print(f"ERROR: {errorIndication}")
                continue

            elif errorStatus:
                authLog.error(f"Device: {validDeviceIP} got an error tesing SNMPv3 user: {user}, error #2: {errorStatus}")
                print(f"ERROR: {errorStatus}")
                print(
                    "{} at {}".format(
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                    )
                )
                continue

            else:
                for varBind in varBinds:
                    print(" = ".join([x.prettyPrint() for x in varBind]))
                authLog.error(f"Device: {validDeviceIP} successfully ran the snmpwalk, output: {varBind}")
                return user, snmpCredentials
        
        return None,None

    except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.error(traceback.format_exc())
        
    