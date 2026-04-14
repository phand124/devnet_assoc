import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

host = os.getenv('NX_HOST')
username = os.getenv('NX_USERNAME')
password = os.getenv('NX_PASSWORD')

# Get device inventory
inventory_url = f'https://{host}/api/v1/show/inventory'
inventory_response = requests.get(
    inventory_url, auth=(username, password), verify=False).json()

# Get system version
version_url = f'https://{host}/api/v1/show/version'
version_response = requests.get(
    version_url, auth=(username, password), verify=False).json()

# Write output to file
output = {
    'inventory': inventory_response,
    'version': version_response
}

output_file = Path(__file__).parent / 'output.json'
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)
