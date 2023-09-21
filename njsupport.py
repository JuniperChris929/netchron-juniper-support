# Developed by Christian Scholz [Mail: chs@ip4.de, Mastodon: @chsjuniper@mastodon.social, Twitter: @chsjuniper]
# Feel free to use and modify this script as needed but use at your own risk!
# This is a hobby project - I'm not employed by Juniper.
# I just wanted a tool that helps me doing my every day work a bit faster and more consistent
# You've been warned ;)

import os
import sys
import time
import shutil
import getpass
import logging
import paramiko
from pathlib import Path
from scp import SCPClient
from jnpr.junos import Device
from datetime import datetime
from jnpr.junos.utils.start_shell import StartShell

varIP = input("Please enter the hostname or IP of your target device: ")
varUser = input("Please enter a username (not root): ")
varPassword = getpass.getpass()
version_arg = "2023.09.21.9773"
now = datetime.now()
dir_config = 'configuration'
dir_rsi = 'rsi'
dir_core = 'core-dumps'
dir_logfiles = 'logfiles'
dir_root = 'upload'
date_arg = now.strftime("%Y-%m-%d_%H-%M-%S")

# pyinstaller -F -i Icon.ico -n Output-Filename script-source.py

# Set up logging
log = "njs_" + date_arg + ".log"
logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

if str(varUser) == 'root':
    sys.exit(
        'Which part of NOT root did you not understand? - Please run the tool again and choose another user.')

while True:
    try:
        varPath = str(input("Do you want the support package [R]emote (on the box) or [L]ocal (download to this PC)?: "))
    except ValueError:
        print("Please choose either R for Remote or L for Local")
    else:
        if varPath=="R" or varPath=="L":
            break
        else:
            print("Please choose either R for Remote or L for Local")

buff = ''
resp = ''
print("\n")
print("\n")
print("\n")
print("###############################################################################")
print("#                          Version:", version_arg, "                          #")
print("#    This script will run all necessary troubleshooting commands for you.     #")
print("#                                                                             #")
print("#            WARNING: Please leave this window open and running.              #")
print("#                                                                             #")
print("#      After the program is finished, it will automatically close itself.     #")
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
ssh.connect(varIP, username=varUser, password=varPassword)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
channel = ssh.invoke_shell()

stdin, stdout, stderr = ssh.exec_command('show virtual-chassis status | match fpc', get_pty=True)
vcmember_list = []
for line in iter(stdout.readline, ""):
    vcmember_list.append(line[0])

# Creating necessary folders (if they don't exist) so root folder does not get messy
logging.info('Trying to create necessary folders')

if not os.path.exists(dir_root + '-' + varIP + '-' + date_arg):
    os.mkdir(dir_root + '-' + varIP + '-' + date_arg)
    logging.info('Info: root directory created successfully')
else:
    logging.info('Info: root directory already existed!')

if not os.path.exists(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_config):
    os.mkdir(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_config)
    logging.info('Info: directory for configuration-files created successfully')
else:
    logging.info('Info: directory for configuration-files already existed!')

if not os.path.exists(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_rsi):
    os.mkdir(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_rsi)
    logging.info('Info: directory for rsi-files created successfully')
else:
    logging.info('Info: directory for rsi-files already existed!')

if not os.path.exists(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_core):
    os.mkdir(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_core)
    logging.info('Info: directory for core-dumps created successfully')
else:
    logging.info('Info: directory for core-dumps already existed!')

if not os.path.exists(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_logfiles):
    os.mkdir(dir_root + '-' + varIP + '-' + date_arg + '/' + dir_logfiles)
    logging.info('Info: directory for logfiles created successfully')
else:
    logging.info('Info: directory for logfiles already existed!')

# Saving the config
print("\n")
print("Step 1/5: Saving the active configuration in set-format (including secrets)")
logging.info('Step1/5: Saving the active configuration in set-format (including secrets)')
stdin, stdout, stderr = ssh.exec_command(
    'show configuration | display set | no-more | save /var/tmp/active-config-' + date_arg + '.txt\n')
exit_status = stdout.channel.recv_exit_status()
if exit_status == 0:
    logging.info('Info: Configuration saved successfully.')
else:
    logging.info('Error: Could not save configuration.')

# Creating the RSI (save to file) and wait for it to complete
# See https://www.juniper.net/documentation/en_US/junos/topics/reference/command-summary/request-support-information.html
print("\n")
print("Step 2/5: Creating the RSI")
logging.info('Step 2/5: Creating the RSI')

if len(vcmember_list) == 1:
    stdin, stdout, stderr = ssh.exec_command('request support information | save /var/tmp/rsi-' + date_arg + '.txt\n')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logging.info('Info: RSI created successfully.')
    else:
        logging.info('Error: Could not create RSI. Please check the device manually.')
else:
    stdin, stdout, stderr = ssh.exec_command('request support information all-members | save /var/tmp/rsi_vc-' + date_arg + '.txt\n')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logging.info('Info: RSI created successfully.')
    else:
        logging.info('Error: Could not create RSI. Please check the device manually.')

ssh.close()
# Compressing the Logfiles
# See https://www.juniper.net/documentation/en_US/junos/topics/task/troubleshooting/troubleshooting-logs-compressing.html
print("\n")
print("Step 3/5: Compressing the Logfiles")
logging.info('Step 3/5: Compressing the Logfiles')

if len(vcmember_list) == 1:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(varIP, username=varUser, password=varPassword)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    channel = ssh.invoke_shell()
    stdin, stdout, stderr = ssh.exec_command(
        'file archive compress source /var/log/* destination /var/tmp/logfiles-' + date_arg + '.tgz\n')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logging.info('Info: Logfiles compressed successfully.')
        ssh.close()
    else:
        logging.info('Error: Logfiles not compressed successfully. Check Device manually.')
        ssh.close()
else:
    for i in vcmember_list:
        dev_ntest = Device(host=varIP, user=varUser, password=varPassword,normalize=True)
        try: 
            dev_ntest.open()
            with StartShell(dev_ntest) as bsd:
                bsd.run('rlogin -Ji fpc' + str(i), timeout=1)
                bsd.wait_for(this='Password:', timeout=1)
                bsd.send(varPassword)
                bsd.run('start shell', timeout=1)
                bsd.wait_for(this='%', timeout=1)
                bsd.run('tar -zcvf /var/tmp/varlog-mem' + str(i) + '.tar.gz /var/log/* ')
                bsd.wait_for(this='%', timeout=1)
                bsd.run('cli -c "file copy /var/tmp/varlog-mem' + str(i) + '.tar.gz fpc'+ str(varVCID_master) +':/var/tmp/"')
                bsd.wait_for(this='%', timeout=1)
            dev_ntest.close()
        except:
            logging.info('Error: VC-Logfiles not compressed successfully. Check Device manually.')
            dev_ntest.close()
# Make single archive for VC
dev_ntest = Device(host=varIP, user=varUser, password=varPassword,normalize=True)
dev_ntest.open()
with StartShell(dev_ntest) as bsd:
    bsd.run('tar -zcvf /var/tmp/varlog-all-vc-members-' + date_arg + '.tar.gz /var/tmp/varlog-mem* ', timeout=1)
    bsd.wait_for(this='%', timeout=1)
dev_ntest.close()    

if varPath == "L":
    # Now downloading all the files created on the device via scp
    print("\n")
    print("Step 4/5: Fetching the files created earlier")
    logging.info('Step 4/5: Fetching the files created earlier')
    logging.info('Info: Fetching RSI...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(varIP, username=varUser, password=varPassword)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    channel = ssh.invoke_shell()

    if len(vcmember_list) == 1:
        try:
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                scp.get(remote_path='/var/tmp/rsi-' + date_arg + '.txt',
                        local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_rsi + '/')
        except:
            logging.info('Error: Could not fetch RSI - something went wrong...')
            scp.close()
        finally:
            logging.info('Info: RSI successfully fetched.')
            scp.close()
    else:
        try:
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                scp.get(remote_path='/var/tmp/rsi_vc-' + date_arg + '.txt',
                        local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_rsi + '/')
        except:
            logging.info('Error: Could not fetch RSI - something went wrong...')
            scp.close()
        finally:
            logging.info('Info: RSI successfully fetched.')
            scp.close()
            
    logging.info('Info: Fetching Logfiles...')
    if len(vcmember_list) == 1:
        try:
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                scp.get(remote_path='/var/tmp/logfiles-' + date_arg + '.tgz',
                        local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_logfiles + '/')
        except:
            logging.info('Error: Could not fetch Logfiles - something went wrong...')
            scp.close()
        finally:
            logging.info('Info: Logfiles successfully fetched.')
            scp.close()
    else:
        try:
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                scp.get(remote_path='/var/tmp/varlog-all-vc-members-' + date_arg + '.tar.gz',
                        local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_logfiles + '/')
        except:
            logging.info('Error: Could not fetch Logfiles - something went wrong...')
            scp.close()
        finally:
            logging.info('Info: Logfiles successfully fetched.')
            scp.close()

    logging.info('Info: Fetching Configuration...')
    try:
        with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
            scp.get(remote_path='/var/tmp/active-config-' + date_arg + '.txt',
                    local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_config + '/')
    except:
        logging.info('Error: Could not fetch active Configuration - something went wrong...')
        scp.close()
    finally:
        logging.info('Info: Configuration successfully fetched.')
        scp.close()
  
    logging.info('Info: Now fetching the crash-dumps (core-dumps) if they exist...')
    try:
        with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
            scp.get(remote_path='/var/crash/*',
                    local_path='./' + dir_root + '-' + varIP + '-' + date_arg + '/' + dir_core + '/')
    except:
        logging.info('Info: No crash-dumps (core-dumps) found - this is a good sign.')
        scp.close()
    finally:
        logging.info('Warning: crash-dumps (core-dumps) found and transferred...')
        scp.close()

    print("\n")
    print("Step 5/5: Deleting files from remote device to gain space back and finishing script")
    logging.info('Step 5/5: Deleting files from remote device to gain space back and finishing script')
    logging.info('Info: Deleting /var/tmp/rsi-' + date_arg + '.txt')
    channel.send('file delete /var/tmp/rsi-' + date_arg + '.txt\n')
    logging.info('Info: File deleted successfully.')
    time.sleep(2)
    logging.info('Info: Deleting /var/tmp/rsi_vc-' + date_arg + '.txt')
    channel.send('file delete /var/tmp/rsi_vc-' + date_arg + '.txt\n')
    logging.info('Info: File deleted successfully.')
    time.sleep(2)
    logging.info('Info: Deleting /var/tmp/logfiles-' + date_arg + '.tgz')
    channel.send('file delete /var/tmp/logfiles-' + date_arg + '.tgz\n')
    logging.info('Info: File deleted successfully.')
    time.sleep(2)
    logging.info('Info: Deleting /var/tmp/varlog-*')
    channel.send('file delete /var/tmp/varlog-*\n')
    logging.info('Info: File deleted successfully.')
    time.sleep(2)
    logging.info('Info: Deleting /var/tmp/active-config-' + date_arg + '.txt')
    channel.send('file delete /var/tmp/active-config-' + date_arg + '.txt\n')
    logging.info('Info: File deleted successfully.')
    resp = channel.recv(9999)
    output = resp.decode().split(',')
    time.sleep(1)
    ssh.close()
    time.sleep(1)
 
    shutil.make_archive('njs-package_' + varIP + '_' + date_arg, 'zip', dir_root + '-' + varIP + '-' + date_arg)
    shutil.rmtree(dir_root + '-' + varIP + '-' + date_arg, ignore_errors=True)
    print("\n")
    print("Finished!")
    pathdisplay = Path(__file__).parent.absolute()
    print("The file has been downloaded to: " + str(pathdisplay))
  
elif varPath == "R":
    print("\n")
    print("Step 4/5 and 5/5: Skipping this steps because you selected that the file should remain on the box.")
    logging.info('Step 4/5 and 5/5: Skipping this steps because you selected that the file should remain on the box.')
    print("The package can be found at /var/tmp/")
    logging.info('The package can be found at /var/tmp/')
    print("\n")
    print("Finished!")
else:
    print("\n")
    print("Error: Something went horribly wrong for reasons we do not know yet. Exiting...")
    logging.info('Error: Something went horribly wrong for reasons we do not know yet. Exiting...')