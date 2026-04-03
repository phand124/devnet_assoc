# Baseline test for containerlab environment.
# Requirements: 
#  - Use netmiko to connect to nodes in the topology. 
#  - Must read the IPs from yaml file, not be hardcoded. 
#  - Return the restults of `show version` for each device. 

import yaml
from netmiko import ConnectHandler

def main():

    file_path = input("Enter the filepath of topology file:")

    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        
        nodes = data.get("topology",{}).get("nodes",{})

        print(f"{'Device Name':<15} | {'Management IP':<15} | {'Version Info'}")
        print("-" * 60)


        for name, config in nodes.items():
            mgmt_ip = config.get("mgmt-ipv4")
            clab_kind = config.get("kind")

            kind_map = {
                    "cisco_iol": "cisco_ios",
                    "nokia_srlinux": "nokia_sros",
                    "ceos": "arista_eos",
                    "linux": "linux"
                    }
    
            netmiko_type = kind_map.get(clab_kind, clab_kind)


            if not mgmt_ip:
                print(f"Skipping {name}, no IP found")
                continue

            device = {
                    "device_type": netmiko_type,
                    "host" : mgmt_ip,
                    "username": "admin",
                    "password": "admin"
                    }
            try:
                with ConnectHandler(**device) as net_connect:
                    output = net_connect.send_command("show version")
                    first_line = output.splitlines()[0] if output else "No output"

                    print(f"{name:<15} | {mgmt_ip:<15} | {first_line}")


            except Exception as e:
                print(f"{name:<15} | {mgmt_ip:<15} | Error: {e}")



    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")


if __name__ == "__main__":
    main()
