# Developed by Christian Scholz [chs@ip4.de]

import paramiko
import time
import sys
import getpass
import logging
import os
from scp import SCPClient
from datetime import datetime


hostname_arg = input("Host: ")
username_arg = input("User: ")
password_arg = getpass.getpass()
version_arg = "3.7.0"
now = datetime.now()
dir_config = 'configuration'
dir_RSI = 'rsi'
dir_core = 'core-dumps'
dir_logfiles = 'logfiles'

# Set up logging
log = "njsupport-live.log"
logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


buff = ''
resp = ''
print("\n")
print("\n")
print("\n")
print("njsupport Version",version_arg,"developed by Christian Scholz")
print("This Script will run all necessary commands for you.")
print("\n")
print("WARNING: Please leave this Window open and running.")
print("\n")
print("After the Process is finished, this Program will automatically close itself.")
print("The files will be in the same folder as this program.")
print("\n")
print("START: [Script started]")
logging.info('START: [Script started]')
time.sleep(2)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname_arg, username=username_arg, password=password_arg)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
channel = ssh.invoke_shell()


# Creating necessary folders (if they don't exist) so root folder does not get messy

if not os.path.exists(dir_config):
    os.mkdir(dir_config)
    logging.info('Info: directory for configuration-files created succesfully')
else:    
    logging.info('Info: directory for configuration-files already existed!')

if not os.path.exists(dir_RSI):
    os.mkdir(dir_RSI)
    logging.info('Info: directory for rsi-files created succesfully')
else:    
    logging.info('Info: directory for rsi-files already existed!')

if not os.path.exists(dir_core):
    os.mkdir(dir_core)
    logging.info('Info: directory for core-dumps created succesfully')
else:    
    logging.info('Info: directory for core-dumps already existed!')

if not os.path.exists(dir_logfiles):
    os.mkdir(dir_logfiles)
    logging.info('Info: directory for logfiles created succesfully')
else:    
    logging.info('Info: directory for logfiles already existed!')


# Deleting files with the same name so we don't fetch old junk
print("\n")
print("Step 1/6: Setting up the environment and creating local folders")
logging.info('Step1/6: Setting up the environment and creating local folders')
logging.info('Info: Deleting /var/tmp/RSI.txt')
channel.send('file delete /var/tmp/RSI.txt\n')
logging.info('File deleted succesfully or file not found (both is fine).')
time.sleep(2)
logging.info('Info: Deleting /var/tmp/logfiles.tgz')
channel.send('file delete /var/tmp/logfiles.tgz\n')
logging.info('File deleted succesfully or file not found (both is fine).')
time.sleep(2)
logging.info('Info: Deleting /var/tmp/active-config.txt')
channel.send('file delete /var/tmp/active-config.txt\n')
logging.info('File deleted succesfully or file not found (both is fine).')
time.sleep(2)

# Saving the config
print("\n")
print("Step 2/6: Saving the active configuration")
logging.info('Step2/6: Saving the active configuration')


stdin, stdout, stderr = ssh.exec_command('show configuration | display set | no-more | save /var/tmp/active-config.txt\n')  
exit_status = stdout.channel.recv_exit_status()          
if exit_status == 0:
    logging.info('Info: Configuration saved succesfully.')
else:
    logging.info('Error: Could not save configuration.')


time.sleep(2)


# Creating the RSI and wait for it to complete
print("\n")
print("Step 3/6: Creating the RSI")
logging.info('Step 3/6: Creating the RSI')

stdin, stdout, stderr = ssh.exec_command('request support information | save /var/tmp/RSI.txt\n')  
exit_status = stdout.channel.recv_exit_status()          
if exit_status == 0:
    logging.info('Info: RSI created succesfully.')
else:
    logging.info('Error: Could not create RSI. Please check the Device manually.')

time.sleep(2)

# Compressing the Logfiles
print("\n")
print("Step 4/6: Compressing the Logfiles")
logging.info('Step 4/6: Compressing the Logfiles')

stdin, stdout, stderr = ssh.exec_command('file archive compress source /var/log/* destination /var/tmp/logfiles.tgz\n')  
exit_status = stdout.channel.recv_exit_status()          
if exit_status == 0:
    logging.info('Info: Logfiles compressed succesfully.')
else:
    logging.info('Error: Logfiles not compresses succesfully. Check Device manually.')

time.sleep(2)


print("\n")
print("Step 5/6: Fetching the files created earlier")
logging.info('Step 5/6: Fetching the files created earlier')

# SCP-Client takes a paramiko transport as an argument

logging.info('Info: Fetching RSI...')

try:
  with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path='/var/tmp/RSI.txt', local_path='./rsi/')
except:
  logging.info('Error: Could not fetch RSI - something went wrong. Horribly...')
  scp.close()
finally:
  logging.info('Info: RSI succesfully fetched.')
  scp.close()


logging.info('Info: Fetching Logfiles...')

try:
  with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path='/var/tmp/logfiles.tgz', local_path='./logfiles/')
except:
  logging.info('Error: Could not fetch Logfiles - something went wrong. Horribly...')
  scp.close()
finally:
  logging.info('Info: Logfiles succesfully fetched.')
  scp.close()
  


logging.info('Info: Fetching Configuration...')

try:
  with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path='/var/tmp/active-config.txt', local_path='./configuration/')
except:
  logging.info('Error: Could not fetch active Configuration - something went wrong. Horribly...')
  scp.close()
finally:
  logging.info('Info: Configuration succesfully fetched.')
  scp.close()



logging.info('Info: Now fetching the Coredumps...')

try:
  with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
        scp.get(remote_path='/var/crash/*', local_path='./Core-Dumps/')
except:
  logging.info('Info: No Coredumps found.')
  scp.close()
finally:
  logging.info('Warning: Coredumps found and transfered...')
  scp.close()


# Deleting old junk
print("\n")
print("Step 6/6: Deleting files from remote device to gain space back and finishing script")
logging.info('Step 6/6: Deleting files from remote device to gain space back and finishing script')
logging.info('Info: Deleting /var/tmp/RSI.txt')
channel.send('file delete /var/tmp/RSI.txt\n')
logging.info('Info: File deleted succesfully.')
time.sleep(2)
logging.info('Info: Deleting /var/tmp/logfiles.tgz')
channel.send('file delete /var/tmp/logfiles.tgz\n')
logging.info('Info: File deleted succesfully.')
time.sleep(2)
logging.info('Info: Deleting /var/tmp/active-config.txt')
channel.send('file delete /var/tmp/active-config.txt\n')
logging.info('Info: File deleted succesfully.')
time.sleep(2)
resp = channel.recv(9999)
output = resp.decode().split(',')
# print(''.join(output)) #commented out so its not shown on the console (debug)
time.sleep(2)
ssh.close()
time.sleep(1)
print("\n")
print("FINISH: [Script ended]")
logging.info('FINISH: [Script ended]')
