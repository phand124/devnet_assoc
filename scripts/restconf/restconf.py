import requests
import json

# ──────────────────────────────────────────────
# Device connection variables — update these
# ──────────────────────────────────────────────
DEVICE_IP = "devnetsandboxiosxec8k.cisco.com"       # Target Cisco XE device IP or hostname
USERNAME   = "admin"             # RESTCONF username
PASSWORD   = "password"     # RESTCONF password
PORT       = 443                 # Default RESTCONF port (443 for HTTPS)
# ──────────────────────────────────────────────

BASE_URL = f"https://{DEVICE_IP}:{PORT}/restconf/data"

HEADERS = {
    "Accept":       "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def get_interfaces() -> dict:
    """
    Retrieve all interfaces from the device using the
    ietf-interfaces YANG model via RESTCONF.
    """
    url = f"{BASE_URL}/ietf-interfaces:interfaces"

    response = requests.get(
        url,
        auth=(USERNAME, PASSWORD),
        headers=HEADERS,
        verify=False,   # Set to True (or a CA bundle path) in production
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def display_interfaces(data: dict) -> None:
    """Parse and print a summary of each interface."""
    interfaces = data.get("ietf-interfaces:interfaces", {}).get("interface", [])

    if not interfaces:
        print("No interfaces found.")
        return

    print(f"\n{'Name':<30} {'Type':<45} {'Enabled'}")
    print("-" * 85)

    for iface in interfaces:
        name    = iface.get("name", "N/A")
        if_type = iface.get("type", "N/A").replace("iana-if-type:", "")
        enabled = iface.get("enabled", "N/A")
        print(f"{name:<30} {if_type:<45} {enabled}")


def main():
    print(f"Connecting to {DEVICE_IP}:{PORT} ...")

    try:
        data = get_interfaces()
        display_interfaces(data)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {DEVICE_IP}:{PORT}. Check IP/reachability.")
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e.response.status_code} — {e.response.text}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    # Suppress SSL warnings when verify=False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
