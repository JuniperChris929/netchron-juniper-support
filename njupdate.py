# Developed by Christian Scholz [Mail: chs@ip4.de, Twitter: @chsjuniper]
# Feel free to use and modify this script as needed
# Use at your own risk
# This is a hobby project - I'm currently not employed by Juniper
# I just wanted a tool that helps me doing my every day work a bit faster and more consistent
# Also I'm new to python so this code can possibly be optimized to do more in less lines ;)

import paramiko
import time
import sys
import getpass
import logging
import os
from scp import SCPClient
from datetime import datetime

software_arg = input("Please enter the Filename of your Software: ")
hostname_arg = input("Please enter the Hostname or IP of your target Device: ")
username_arg = input("Please Enter a Username (not root): ")
password_arg = getpass.getpass()
version_arg = "2020.05.10.20"
now = datetime.now()
dir_sw = 'software'
dir_logfiles = 'logfiles'
dir_root = 'update'
date_arg = now.strftime("%Y-%m-%d_%H-%M-%S")

# Set up logging
log = "nju.log"
logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

if str(username_arg) == 'root':
    sys.exit(
        'Unfortunately the user root is currently not supported - Please run the tool again and choose another user.')

buff = ''
resp = ''
print("\n")
print("\n")
print("\n")
print("###############################################################################")
print("#                      NJUpdate version", version_arg, "                       #")
print("#         This script will run all necessary update commands for you.         #")
print("#                                                                             #")
print("#            WARNING: Please leave this Window open and running.              #")
print("#                                                                             #")
print("#      After the Program is finished, it will automatically close itself.     #")
print("#                                                                             #")
print("#        DO NOT POWER DOWN YOUR DEVICE WHILE THE SCRIPT IS RUNNING!!!!        #")
print("#                                                                             #")
print("###############################################################################")
print("\n")
print("\n")
print("\n")
print("Script is starting...")
logging.info('Script is starting...')
time.sleep(2)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname_arg, username=username_arg, password=password_arg)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
channel = ssh.invoke_shell()

# Creating necessary folders (if they don't exist) so root folder does not get messy
logging.info('Trying to create necessary folders')

if not os.path.exists(dir_root + '-' + hostname_arg + '-' + date_arg):
    os.mkdir(dir_root + '-' + hostname_arg + '-' + date_arg)
    logging.info('Info: root directory created successfully')
else:
    logging.info('Info: root directory already existed!')

if not os.path.exists(dir_root + '-' + hostname_arg + '/' + dir_sw + '/' + software_arg):
    logging.info('Critical: could not find software directory - aborting!')
else:
    logging.info('Info: directory for software is visible to the script!')

if not os.path.exists(dir_root + '-' + hostname_arg + '-' + date_arg + '/' + dir_logfiles):
    os.mkdir(dir_root + '-' + hostname_arg + '-' + date_arg + '/' + dir_logfiles)
    logging.info('Info: directory for logfiles created successfully')
else:
    logging.info('Info: directory for logfiles already existed!')


# Compressing the Logfiles
# https://www.juniper.net/documentation/en_US/junos/topics/task/troubleshooting/troubleshooting-logs-compressing.html
print("\n")
print("Step 1: Compressing the Logfiles")
logging.info('Step 1: Compressing the Logfiles')
stdin, stdout, stderr = ssh.exec_command(
    'file archive compress source /var/log/* destination /var/tmp/logfiles-' + date_arg + '.tgz\n')
exit_status = stdout.channel.recv_exit_status()
if exit_status == 0:
    logging.info('Info: Logfiles compressed successfully.')
else:
    logging.info('Error: Logfiles not compresses successfully. Check Device manually.')


print("\n")
print("Step 2: Fetching the Logfiles")
logging.info('Step 2: Fetching the Logfiles')
try:
    with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path='/var/tmp/logfiles-' + date_arg + '.tgz',
                local_path='./' + dir_root + '-' + hostname_arg + '-' + date_arg + '/' + dir_logfiles + '/')
except:
    logging.info('Error: Could not fetch Logfiles - something went wrong...')
    scp.close()
finally:
    logging.info('Info: Logfiles successfully fetched.')
    scp.close()


# STEP3: Cleanup - NEED TO CHECK HOW TO SAY YES ON CLI
print("\n")
print("Step 3: Cleaning the Storage")

print("\n")
print("Step 4: Uploading Software to Device")
logging.info('Step 4: Uploading Software to Device')
try:
    with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.put(dir_sw + '/' + software_arg, '/var/tmp/' + software_arg, )
except:
    logging.info('Error: Could not place file - something went wrong...')
    scp.close()
finally:
    logging.info('Info: File added!')
    scp.close()


# Deleting our files on the switch so we don't exhaust all the space on it
print("\n")
print("Step 5: Adding new software and reboot")
logging.info('Step 5: Adding new software and reboot')
logging.info('Info: request system software add no-validate no-copy unlink reboot /var/tmp/' + software_arg + '\n')
channel.send('request system software add no-validate no-copy unlink reboot /var/tmp/' + software_arg + '\n')
logging.info('Info: Command sent - let us pray to the lord now and hope it gets back...')
time.sleep(1)



resp = channel.recv(9999)
output = resp.decode().split(',')
# print(''.join(output)) #commented out so its not shown on the console (debug)
time.sleep(300)

ssh.close()


print("\n")
print("Finishing the script...")
logging.info('Finishing the script...')
print("\n")
print("Done - enjoy your updated Device!")
logging.info('Done - enjoy your updated Device!')