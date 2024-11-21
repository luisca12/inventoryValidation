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

# 1.3.6.1.2.1.4.28.1 # 1.3.6.1.2.1.1
async def snmpWalkv3(target):
    """
    Perform an SNMPv3 walk.

    :param target: The SNMP device IP or hostname.
    :param user: The SNMPv3 username.
    :param auth_key: The SNMPv3 authentication key (password).
    :param priv_key: The SNMPv3 privacy (encryption) key.
    :param oids: List of OIDs to walk, e.g. ['1.3.6.1.2.1.2.2.1']
    :return: None
    """
    oid="1.3.6.1.2.1.1.3"
    
    snmpCredentials = {
        'user1': ['authPass1','privPass1'],
        'user2': ['authPass2','privPass2'],
        'user3': ['authPass3','privPass3']
    }

    for user in snmpCredentials.keys():
        print(f"User: {user}")
        
        authPass = snmpCredentials[user][0]
        privPass = snmpCredentials[user][1]

        print(f"authPass: {authPass}")
        print(f"privPass: {privPass}")

    
        # Create the SNMPv3 context
        iterator = await next_cmd(
            SnmpEngine(),
            UsmUserData(
                user, 
                authKey=authPass, 
                privKey=privPass, 
                authProtocol=usmHMACSHAAuthProtocol, 
                privProtocol=usmAesCfb128Protocol),
            await UdpTransportTarget.create((target, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = iterator

        if errorIndication:
            print(errorIndication)
            return False

        elif errorStatus:
            print(
                "{} at {}".format(
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                )
            )
            return False

        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
            return False
        
    return user, snmpCredentials