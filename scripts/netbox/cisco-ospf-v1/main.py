import os
import requests
from dotenv import load_dotenv

load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL")
TOKEN = os.getenv("NETBOX_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def get_or_create(endpoint, lookup_params, data):
    """Check if object exists by lookup_params, create if not."""
    url = f"{NETBOX_URL}/api/{endpoint}/"
    
    # Check if exists
    response = requests.get(url, headers=HEADERS, params=lookup_params)
    response.raise_for_status()
    results = response.json()["results"]
    
    if results:
        print(f"EXISTS: {endpoint} — {lookup_params}")
        return results[0]
    
    # Create if not
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(f"CREATED: {endpoint} — {data}")
    return response.json()


# ── Tenant ────────────────────────────────────────────────────────────────────

tenant = get_or_create(
    "tenancy/tenants",
    {"slug": "cisco-ospf-v1"},
    {"name": "cisco-ospf-v1", "slug": "cisco-ospf-v1"}
)

# ── Sites ─────────────────────────────────────────────────────────────────────

sites = [
    {"name": "ospf-hq",      "slug": "ospf-hq"},
    {"name": "ospf-branch1", "slug": "ospf-branch1"},
    {"name": "ospf-branch2", "slug": "ospf-branch2"},
]

site_objects = {}
for s in sites:
    obj = get_or_create(
        "dcim/sites",
        {"slug": s["slug"]},
        {**s, "status": "active", "tenant": tenant["id"]}
    )
    site_objects[s["slug"]] = obj

# ── Prefix ────────────────────────────────────────────────────────────────────

prefix = get_or_create(
    "ipam/prefixes",
    {"prefix": "192.168.110.0/24"},
    {
        "prefix": "192.168.110.0/24",
        "status": "active",
        "tenant": tenant["id"],
    }
)

# ── Devices ───────────────────────────────────────────────────────────────────

# Get device type and role IDs needed for device creation
def get_id(endpoint, slug):
    url = f"{NETBOX_URL}/api/{endpoint}/"
    r = requests.get(url, headers=HEADERS, params={"slug": slug})
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Not found: {endpoint} slug={slug}")
    return results[0]["id"]

iol_l3_id  = get_id("dcim/device-types", "cisco-iol-l3")
iol_l2_id  = get_id("dcim/device-types", "cisco-iol-l2")
router_id  = get_id("dcim/device-roles", "router")
switch_id  = get_id("dcim/device-roles", "switch")

devices = [
    # HQ
    {"name": "core1",    "site": "ospf-hq",      "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.11/24"},
    {"name": "core2",    "site": "ospf-hq",      "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.12/24"},
    {"name": "hq-dist",  "site": "ospf-hq",      "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.13/24"},
    {"name": "hq-acc1",  "site": "ospf-hq",      "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.14/24"},
    {"name": "hq-acc2",  "site": "ospf-hq",      "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.15/24"},
    # Branch1
    {"name": "br1-wan",  "site": "ospf-branch1", "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.21/24"},
    {"name": "br1-dist", "site": "ospf-branch1", "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.22/24"},
    {"name": "br1-acc1", "site": "ospf-branch1", "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.23/24"},
    {"name": "br1-acc2", "site": "ospf-branch1", "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.24/24"},
    # Branch2
    {"name": "br2-wan",  "site": "ospf-branch2", "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.31/24"},
    {"name": "br2-dist", "site": "ospf-branch2", "type": iol_l3_id, "role": router_id, "mgmt_ip": "192.168.110.32/24"},
    {"name": "br2-acc1", "site": "ospf-branch2", "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.33/24"},
    {"name": "br2-acc2", "site": "ospf-branch2", "type": iol_l2_id, "role": switch_id, "mgmt_ip": "192.168.110.34/24"},
]

for d in devices:
    site_id = site_objects[d["site"]]["id"]

    # Create device
    device = get_or_create(
        "dcim/devices",
        {"name": d["name"]},
        {
            "name": d["name"],
            "device_type": d["type"],
            "role": d["role"],
            "site": site_id,
            "tenant": tenant["id"],
            "status": "active",
        }
    )

    # Create Management0 interface
    iface = get_or_create(
        "dcim/interfaces",
        {"device_id": device["id"], "name": "Management0"},
        {
            "device": device["id"],
            "name": "Management0",
            "type": "virtual",
        }
    )

    # Create IP address
    ip = get_or_create(
        "ipam/ip-addresses",
        {"address": d["mgmt_ip"], "interface_id": iface["id"]},
        {
            "address": d["mgmt_ip"],
            "status": "active",
            "tenant": tenant["id"],
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": iface["id"],
        }
    )

    # Set as primary IP on device if not already set
    if not device.get("primary_ip4"):
        requests.patch(
            f"{NETBOX_URL}/api/dcim/devices/{device['id']}/",
            headers=HEADERS,
            json={"primary_ip4": ip["id"]}
        ).raise_for_status()
        print(f"PRIMARY IP SET: {d['name']} → {d['mgmt_ip']}")


print("\nDone.")
