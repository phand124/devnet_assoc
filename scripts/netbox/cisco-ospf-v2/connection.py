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

# ── Lab Connections ───────────────────────────────────────────────────────────

LAB = {
    "tenant": "cisco-ospf-v2",
    "links": [
        ("core1",    "Ethernet0/1", "core2",    "Ethernet0/1"),
        ("core1",    "Ethernet0/2", "hq-dist",  "Ethernet0/1"),
        ("core2",    "Ethernet0/2", "hq-dist",  "Ethernet0/2"),
        ("core1",    "Ethernet0/3", "br1-wan",  "Ethernet0/1"),
        ("core2",    "Ethernet0/3", "br2-wan",  "Ethernet0/1"),
        ("hq-dist",  "Ethernet0/3", "hq-acc1",  "Ethernet0/1"),
        ("hq-dist",  "Ethernet1/0", "hq-acc2",  "Ethernet0/1"),
        ("br1-wan",  "Ethernet0/2", "br1-dist", "Ethernet0/1"),
        ("br1-dist", "Ethernet0/2", "br1-acc1", "Ethernet0/1"),
        ("br1-dist", "Ethernet0/3", "br1-acc2", "Ethernet0/1"),
        ("br2-wan",  "Ethernet0/2", "br2-dist", "Ethernet0/1"),
        ("br2-dist", "Ethernet0/2", "br2-acc1", "Ethernet0/1"),
        ("br2-dist", "Ethernet0/3", "br2-acc2", "Ethernet0/1"),
    ]
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_device_id(name, tenant_slug):
    url = f"{NETBOX_URL}/api/dcim/devices/"
    r = requests.get(url, headers=HEADERS, params={"name": name, "tenant": tenant_slug})
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Device not found: {name} in tenant {tenant_slug}")
    return results[0]["id"]


def get_or_create_interface(device_id, iface_name):
    url = f"{NETBOX_URL}/api/dcim/interfaces/"
    r = requests.get(url, headers=HEADERS, params={"device_id": device_id, "name": iface_name})
    r.raise_for_status()
    results = r.json()["results"]
    if results:
        print(f"  EXISTS  interface — {iface_name} on device {device_id}")
        return results[0]
    r = requests.post(url, headers=HEADERS, json={
        "device": device_id,
        "name":   iface_name,
        "type":   "virtual"
    })
    r.raise_for_status()
    print(f"  CREATED interface — {iface_name} on device {device_id}")
    return r.json()


def cable_exists(iface_a_id, iface_b_id):
    url = f"{NETBOX_URL}/api/dcim/cables/"
    for iface_id in [iface_a_id, iface_b_id]:
        for side in ["termination_a_id", "termination_b_id"]:
            r = requests.get(url, headers=HEADERS, params={side: iface_id})
            r.raise_for_status()
            if r.json()["results"]:
                return True
    return False


def create_cable(iface_a_id, iface_b_id):
    if cable_exists(iface_a_id, iface_b_id):
        print(f"  EXISTS  cable — iface {iface_a_id} ↔ iface {iface_b_id}")
        return
    url = f"{NETBOX_URL}/api/dcim/cables/"
    r = requests.post(url, headers=HEADERS, json={
        "a_terminations": [{"object_type": "dcim.interface", "object_id": iface_a_id}],
        "b_terminations": [{"object_type": "dcim.interface", "object_id": iface_b_id}],
    })
    r.raise_for_status()
    print(f"  CREATED cable — iface {iface_a_id} ↔ iface {iface_b_id}")


_device_cache = {}

def cached_device_id(name, tenant_slug):
    key = f"{tenant_slug}:{name}"
    if key not in _device_cache:
        _device_cache[key] = get_device_id(name, tenant_slug)
    return _device_cache[key]


# ── Main ──────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Processing connections for: {LAB['tenant']}")
print(f"{'='*60}")

for dev_a, iface_a, dev_b, iface_b in LAB["links"]:
    print(f"\n  → {dev_a}:{iface_a} ↔ {dev_b}:{iface_b}")

    dev_a_id = cached_device_id(dev_a, LAB["tenant"])
    dev_b_id = cached_device_id(dev_b, LAB["tenant"])

    iface_a_obj = get_or_create_interface(dev_a_id, iface_a)
    iface_b_obj = get_or_create_interface(dev_b_id, iface_b)

    create_cable(iface_a_obj["id"], iface_b_obj["id"])

print("\n\nDone.")
