#!/usr/bin/env python3

import requests
import json
from requests.exceptions import RequestException
import sys
from tabulate import tabulate
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# vManage connection details
VMANAGE_HOST = "https://sandbox-sdwan-2.cisco.com"
USERNAME = "devnetuser"
PASSWORD = "RG!_Yw919_83"

def authenticate(vmanage_host, username, password):
    """Authenticate to vManage and get session token"""
    base_url_str = f'{vmanage_host}/j_security_check'

    try:
        # Format data for authentication
        login_data = {'j_username': username, 'j_password': password}
        
        # Create session
        session = requests.session()
        
        # Send authentication request
        response = session.post(url=base_url_str, data=login_data, verify=False)
        
        if response.status_code == 200:
            # Get token from response cookies
            if 'JSESSIONID' in session.cookies:
                return session
            else:
                print("Authentication failed: No session token received")
                sys.exit(1)
        else:
            print(f"Authentication failed with status code: {response.status_code}")
            sys.exit(1)
            
    except RequestException as e:
        print(f"Error during authentication: {str(e)}")
        sys.exit(1)

def get_devices(session):
    """Get list of all devices from vManage"""
    url = f"{VMANAGE_HOST}/dataservice/device"
    
    try:
        response = session.get(url, verify=False)
        if response.status_code == 200:
            device_items = response.json()['data']
            return device_items
        else:
            print(f"Failed to get devices. Status code: {response.status_code}")
            return None
            
    except RequestException as e:
        print(f"Error getting devices: {str(e)}")
        return None

def main():
    print("\nConnecting to vManage...")
    session = authenticate(VMANAGE_HOST, USERNAME, PASSWORD)
    print("Successfully authenticated to vManage")
    
    print("\nRetrieving device list...")
    devices = get_devices(session)
    
    if devices:
        # Prepare data for tabulate
        headers = ["Hostname", "System IP", "Model", "Status", "Site ID"]
        table_data = []
        
        for device in devices:
            table_data.append([
                device.get('host-name', 'N/A'),
                device.get('system-ip', 'N/A'),
                device.get('device-model', 'N/A'),
                device.get('status', 'N/A'),
                device.get('site-id', 'N/A')
            ])
        
        # Print devices in table format
        print("\nDevice List:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal devices found: {len(devices)}")
    else:
        print("No devices found or error occurred while retrieving devices.")

if __name__ == "__main__":
    main() 
