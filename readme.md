# XIQ Assign Network Policy
### XIQ_assign_network_policy.py
## Purpose
This script will load a csv file with AP information. Validate that the device is in your XIQ instance by serial number and then check if the network policy matches what is in the csv file. If the network policy does not match and the network policy listed in the csv exists, the network policy will be updated on the device. 

## Information
The script will collect all device and all network policies configured in the XIQ instance. Then will then be compared to what is listed in the csv file. 

## Needed files
The XIQ_assign_network_policy.py script uses several other files. If these files are missing the script will not function.
In the same folder as the XIQ_assign_network_policy.py script there should be an /app/ folder. Inside this folder should be a logger.py file and a xiq_api.py file. After running the script a new file 'Assign_Network_Policy_log.log' will be created.

The log file that is created when running and will show any errors that the script might run into. It is a great place to look when troubleshooting any issues.

## Running the script
open the terminal to the location of the script and run this command.

```
python XIQ_assign_network_policy.py
```
### Logging in
The script will prompt the user for XIQ credentials.
>Note: your password will not show on the screen as you type

### CSV file 
The script will prompt for a csv file. You can drag this into the windows or enter the name of the file. To simplify you can add the file to the same folder as the script to not have to type in the full path. 
>Note: the CSV file must have a '//Serial Number' column with the device serial numbers and a 'Network Policy' column with the network policy names. The device serial numbers and the network policy name must exist in the XIQ instance. 

### flags
There is an optional flag that can be added to the script when running.
```
--external
```
This flag will allow you to create the locations and assign the devices to locations on an XIQ account you are an external user on. After logging in with your XIQ credentials the script will give you a numeric option of each of the XIQ instances you have access to. Choose the one you would like to use.

You can add the flag when running the script.
```
python XIQ_assign_network_policy.py --external
```
## requirements
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.