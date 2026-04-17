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

# ── Lab Definition ────────────────────────────────────────────────────────────

LAB = {
    "tenant":       "cisco-ospf-v2",
    "tenant_slug":  "cisco-ospf-v2",
    "mgmt_prefix":  "192.168.115.0/24",
    "ipv6_parent":  "2001:db8:0089::/48",
    "ipv6_prefix":  "2001:db8:0089:2::/64",
    "sites": {
        "ospf-hq":      "ospf-hq",
        "ospf-branch1": "ospf-branch1",
        "ospf-branch2": "ospf-branch2",
    },
    "devices": [
        {"name": "core1",    "site": "ospf-hq",      "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.11/24", "mgmt_ipv6": "2001:db8:89:2::11/64"},
        {"name": "core2",    "site": "ospf-hq",      "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.12/24", "mgmt_ipv6": "2001:db8:89:2::12/64"},
        {"name": "hq-dist",  "site": "ospf-hq",      "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.13/24", "mgmt_ipv6": "2001:db8:89:2::13/64"},
        {"name": "hq-acc1",  "site": "ospf-hq",      "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.14/24", "mgmt_ipv6": "2001:db8:89:2::14/64"},
        {"name": "hq-acc2",  "site": "ospf-hq",      "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.15/24", "mgmt_ipv6": "2001:db8:89:2::15/64"},
        {"name": "br1-wan",  "site": "ospf-branch1", "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.21/24", "mgmt_ipv6": "2001:db8:89:2::21/64"},
        {"name": "br1-dist", "site": "ospf-branch1", "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.22/24", "mgmt_ipv6": "2001:db8:89:2::22/64"},
        {"name": "br1-acc1", "site": "ospf-branch1", "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.23/24", "mgmt_ipv6": "2001:db8:89:2::23/64"},
        {"name": "br1-acc2", "site": "ospf-branch1", "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.24/24", "mgmt_ipv6": "2001:db8:89:2::24/64"},
        {"name": "br2-wan",  "site": "ospf-branch2", "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.31/24", "mgmt_ipv6": "2001:db8:89:2::31/64"},
        {"name": "br2-dist", "site": "ospf-branch2", "type": "cisco-iol-l3", "role": "router", "mgmt_ipv4": "192.168.115.32/24", "mgmt_ipv6": "2001:db8:89:2::32/64"},
        {"name": "br2-acc1", "site": "ospf-branch2", "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.33/24", "mgmt_ipv6": "2001:db8:89:2::33/64"},
        {"name": "br2-acc2", "site": "ospf-branch2", "type": "cisco-iol-l2", "role": "switch", "mgmt_ipv4": "192.168.115.34/24", "mgmt_ipv6": "2001:db8:89:2::34/64"},
    ]
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_or_create(endpoint, lookup_params, data):
    url = f"{NETBOX_URL}/api/{endpoint}/"
    r = requests.get(url, headers=HEADERS, params=lookup_params)
    r.raise_for_status()
    results = r.json()["results"]
    if results:
        print(f"  EXISTS  {endpoint} — {lookup_params}")
        return results[0]
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()
    print(f"  CREATED {endpoint} — {data.get('name') or data.get('prefix') or data.get('address')}")
    return r.json()


def get_id(endpoint, slug):
    url = f"{NETBOX_URL}/api/{endpoint}/"
    r = requests.get(url, headers=HEADERS, params={"slug": slug})
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Not found: {endpoint} slug={slug}")
    return results[0]["id"]


_id_cache = {}

def cached_id(endpoint, slug):
    key = f"{endpoint}:{slug}"
    if key not in _id_cache:
        _id_cache[key] = get_id(endpoint, slug)
    return _id_cache[key]


# ── Main ──────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Processing lab: {LAB['tenant']}")
print(f"{'='*60}")

# Tenant
tenant = get_or_create(
    "tenancy/tenants",
    {"slug": LAB["tenant_slug"]},
    {"name": LAB["tenant"], "slug": LAB["tenant_slug"]}
)

# Sites
site_objects = {}
for slug, name in LAB["sites"].items():
    obj = get_or_create(
        "dcim/sites",
        {"slug": slug},
        {"name": name, "slug": slug, "status": "active", "tenant": tenant["id"]}
    )
    site_objects[slug] = obj

# IPv4 mgmt prefix
get_or_create(
    "ipam/prefixes",
    {"prefix": LAB["mgmt_prefix"]},
    {"prefix": LAB["mgmt_prefix"], "status": "active", "tenant": tenant["id"]}
)

# IPv6 parent prefix
get_or_create(
    "ipam/prefixes",
    {"prefix": LAB["ipv6_parent"]},
    {"prefix": LAB["ipv6_parent"], "status": "container", "tenant": tenant["id"]}
)

# IPv6 lab prefix
get_or_create(
    "ipam/prefixes",
    {"prefix": LAB["ipv6_prefix"]},
    {"prefix": LAB["ipv6_prefix"], "status": "active", "tenant": tenant["id"]}
)

# Devices
for d in LAB["devices"]:
    print(f"\n  → {d['name']}")

    device_type_id = cached_id("dcim/device-types", d["type"])
    role_id        = cached_id("dcim/device-roles", d["role"])
    site_id        = site_objects[d["site"]]["id"]

    device = get_or_create(
        "dcim/devices",
        {"name": d["name"]},
        {
            "name":        d["name"],
            "device_type": device_type_id,
            "role":        role_id,
            "site":        site_id,
            "tenant":      tenant["id"],
            "status":      "active",
        }
    )

    # Management interface
    iface = get_or_create(
        "dcim/interfaces",
        {"device_id": device["id"], "name": "Management0"},
        {"device": device["id"], "name": "Management0", "type": "virtual"}
    )

    # IPv4 address
    ipv4 = get_or_create(
        "ipam/ip-addresses",
        {"address": d["mgmt_ipv4"], "interface_id": iface["id"]},
        {
            "address":              d["mgmt_ipv4"],
            "status":               "active",
            "tenant":               tenant["id"],
            "assigned_object_type": "dcim.interface",
            "assigned_object_id":   iface["id"],
        }
    )

    # IPv6 address
    ipv6 = get_or_create(
        "ipam/ip-addresses",
        {"address": d["mgmt_ipv6"], "interface_id": iface["id"]},
        {
            "address":              d["mgmt_ipv6"],
            "status":               "active",
            "tenant":               tenant["id"],
            "assigned_object_type": "dcim.interface",
            "assigned_object_id":   iface["id"],
        }
    )

    # Set primary IPs if not already set
    patch = {}
    if not device.get("primary_ip4"):
        patch["primary_ip4"] = ipv4["id"]
    if not device.get("primary_ip6"):
        patch["primary_ip6"] = ipv6["id"]
    if patch:
        requests.patch(
            f"{NETBOX_URL}/api/dcim/devices/{device['id']}/",
            headers=HEADERS,
            json=patch
        ).raise_for_status()
        print(f"  PRIMARY IPs SET: {d['name']} → {d['mgmt_ipv4']} / {d['mgmt_ipv6']}")

print("\n\nDone.")
