from ncclient import manager
import xmltodict
import sys
from typing import Dict, Any
import xml.dom.minidom

# NETCONF filter for interface information
INTERFACE_FILTER = '''
<filter>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name/>
            <description/>
            <enabled/>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                    <ip/>
                    <netmask/>
                </address>
            </ipv4>
        </interface>
    </interfaces>
</filter>
'''

def connect_to_device(host: str, username: str, password: str, port: int = 830) -> manager.Manager:
    """
    Establishes a NETCONF connection to the device.
    """
    try:
        connection = manager.connect(
            host=device_params['host'],
            port=device_params['port'],
            username=device_params['username'],
            password=device_params['Password'],
            hostkey_verify=False,
            device_params={'name': 'csr'}
        )
        return connection
    except Exception as e:
        print(f"Failed to connect to {device_params['host']}: {str(e)}")
        raise

def configure_loopback(connection: manager.Manager) -> None:
    """
    Configures Loopback2 interface with the specified IP address.
    """
    try:
      # Send Configureation to the device
        response = connection.edit_config(target='running', config=LOOPBACK_CONFIG)

        # Pretty print the response
       print("\nConfiguration Result:")
       print(xml.dom.minidom.parseString(response.xml).toprettyxml())
       
       if response.ok:
           print("\nLoopback2 interface configured successfully!")
        else:
           print("\nFailed to configure Loopback2 interface")   
       
    except Exception as e:
        print(f"Error configuring interface: {str(e)}")
         raise


def main():
    # Device connection parameters
    device = {
        'host': '192.168.0.101',  # Replace with your device's IP
        'username': 'admin',     # Replace with your username
        'password': 'password',     # Replace with your password
        'port': 830             # Standard NETCONF port
    }

    try:
          # Connect to the device
          with connect_to_device(device) as conn:
               print(f"Successfully connected to {device['host']}")
               
               #configure the loopback interface
               configure_loopback(conn)
     except exception as e:
         print(f"script execution failed: {str(e)}")   
 if __name__=="__main__":
    main()               
