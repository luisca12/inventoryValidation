import traceback
import socket
import csv
import os

def mkdir():
    path = "logs"
    path1 = "Outputs"
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except Exception as Error:
            print(f"ERROR: Wasn't possible to create new folder \"{path}\"")
            print(traceback.format_exc())
    if not os.path.exists(path1):
        try:
            os.mkdir(path1)
        except Exception as Error:
            print(f"ERROR: Wasn't possible to create new folder \"{path1}\"")
            print(traceback.format_exc())

from log import authLog

def checkConnect22(ipAddress, port=22, timeout=3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connectTest:
            connectTest.settimeout(timeout)
            connectTestOut = connectTest.connect_ex((ipAddress, port))
            return connectTestOut == 0
    except socket.error as error:
        authLog.error(f"Device {ipAddress} is not reachable on port TCP 22.")
        authLog.error(f"Error:{error}\n", traceback.format_exc())
        return False

def logInCSV(validDeviceIP, filename="", *args):
    print(f"INFO: File created: {filename}")
    authLog.info(f"File created: {filename}")
    with open(f'Outputs/{filename}.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([validDeviceIP, *args])
        authLog.info(f"Appended device: {validDeviceIP} to file {filename}")

def genTxtFile(validDeviceIP, username, filename="", *args):
    with open(f"{validDeviceIP} {filename}.txt","a") as failedDevices:
        failedDevices.write(f"User {username} connected to {validDeviceIP}\n\n")
        for arg in args:
            if isinstance(arg, dict):
                for key,values in arg.items():
                    failedDevices.write(f"{key}: ")
                    failedDevices.write(", ".join(str(v) for v in values))
                    failedDevices.write("\n")
            
            elif isinstance(arg, list):
                for item in arg:
                    failedDevices.write(item)
                    failedDevices.write("\n")

            elif isinstance(arg, str):
                failedDevices.write(arg + "\n")