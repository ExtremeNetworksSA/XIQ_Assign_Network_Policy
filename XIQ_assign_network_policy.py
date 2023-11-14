#!/usr/bin/env python3
import logging
import argparse
import os
import sys
import inspect
import getpass
import json
import pandas as pd
import numpy as np
from pprint import pprint as pp
from app.logger import logger
from app.xiq_api import XIQ
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger('AssignNetworkPolicy.Main')

XIQ_API_token = ''

pageSize = 100

parser = argparse.ArgumentParser()
parser.add_argument('--external',action="store_true", help="Optional - adds External Account selection, to use an external VIQ")
args = parser.parse_args()

PATH = current_dir

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0;0m"

def yesNoLoop(question):
    validResponse = False
    while validResponse != True:
        response = input(f"{question} (y/n) ").lower()
        if response =='n' or response == 'no':
            response = 'n'
            validResponse = True
        elif response == 'y' or response == 'yes':
            response = 'y'
            validResponse = True
        elif response == 'q' or response == 'quit':
            sys.stdout.write(RED)
            sys.stdout.write("script is exiting....\n")
            sys.stdout.write(RESET)
            raise SystemExit
    return response

if XIQ_API_token:
    x = XIQ(token=XIQ_API_token)
else:
    print("Enter your XIQ login credentials")
    username = input("Email: ")
    password = getpass.getpass("Password: ")
    x = XIQ(user_name=username,password = password)

#OPTIONAL - use externally managed XIQ account
if args.external:
    accounts, viqName = x.selectManagedAccount()
    if accounts == 1:
        validResponse = False
        while validResponse != True:
            response = input("No External accounts found. Would you like to import data to your network?")
            if response == 'y':
                validResponse = True
            elif response =='n':
                sys.stdout.write(RED)
                sys.stdout.write("script is exiting....\n")
                sys.stdout.write(RESET)
                raise SystemExit
    elif accounts:
        validResponse = False
        while validResponse != True:
            print("\nWhich VIQ would you like to import the floor plan and APs too?")
            accounts_df = pd.DataFrame(accounts)
            count = 0
            for df_id, viq_info in accounts_df.iterrows():
                print(f"   {df_id}. {viq_info['name']}")
                count = df_id
            print(f"   {count+1}. {viqName} (This is Your main account)\n")
            selection = input(f"Please enter 0 - {count+1}: ")
            try:
                selection = int(selection)
            except:
                sys.stdout.write(YELLOW)
                sys.stdout.write("Please enter a valid response!!")
                sys.stdout.write(RESET)
                continue
            if 0 <= selection <= count+1:
                validResponse = True
                if selection != count+1:
                    newViqID = (accounts_df.loc[int(selection),'id'])
                    newViqName = (accounts_df.loc[int(selection),'name'])
                    x.switchAccount(newViqID, newViqName)

print("Make sure the csv file is in the same folder as the python script.")
filename = input("Please enter csv filename: ")
filename = filename.replace("\ ", " ")
filename = filename.replace("'", "")

# Collect data from CSV
csv_df = pd.read_csv(filename,dtype=str)
csv_df['//Serial Number'].replace('', np.nan, inplace=True)

# Collect data for XIQ devices
device_data = x.collectDevices(pageSize)
device_df = pd.DataFrame(device_data)
device_df.set_index('id',inplace=True)

# Collect data for XIQ Network Policies
np_data = x.collectNetworkPolicies(pageSize)
np_df = pd.DataFrame(np_data)
np_df.set_index('id',inplace=True)

print("\n\n")

for index, row in csv_df.iterrows():
    make_change = False
    if str(row['//Serial Number']) in device_df['serial_number'].tolist():
        # If serial number of devices exists in XIQ get the id of the device
        filt = device_df['serial_number'] == row['//Serial Number']
        device_id = device_df.loc[filt].index[0]
        # get the configure network policy of the device in XIQ
        current_np_id = device_df.loc[device_id,'network_policy_id']
        # If network Policy is unassigned Log and make change
        if current_np_id == 0:
            msg = f"Device {device_df.loc[device_id,'hostname']} does not currently have a Network Policy assigned."
            print(msg)
            logger.info(msg)
            make_change = True
        else:
            # get name of configured network Policy
            current_np_name = np_df.loc[current_np_id, 'name']
            if row['Network Policy'] == current_np_name:
                msg = f"Device {device_df.loc[device_id,'hostname']} is currently assigned to the correct Network Policy."
                print(msg)
                logger.info(msg)
            else:
                make_change = True

        # Change network policy for device
        if make_change:
            if row['Network Policy'] not in np_df['name'].tolist():
                msg = f"Network Policy {row['Network Policy']} was not found in XIQ. Please configure and try again"
                print(msg)
                logger.error(msg)
                continue
            else:
                filt = np_df['name'] == row['Network Policy']
                new_np_id = np_df[filt].index[0]
                print(f"Changing {device_df.loc[device_id,'hostname']} to Network Policy {row['Network Policy']} - {new_np_id}...",end='')
                payload = json.dumps({"devices":{"ids":[str(device_id)]},"network_policy_id":str(new_np_id)})
                response = x.changeNetworkPolicy(payload)
                if response != "Success":
                    print("FAILED")
                    logger.error(f"Failed to change {device_df.loc[device_id,'hostname']} to Network Policy {row['Network Policy'] - {new_np_id}}")
                else:
                    logger.info(f"Successfully Changed {device_df.loc[device_id,'hostname']} to Network Policy {row['Network Policy']} - {new_np_id}")
                    print(response)

