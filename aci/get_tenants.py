# aci/ get_tenants.py
# Using the older ACIToolkit, connect to APIC and pull first 15 tenants. 

import os
import sys
from dotenv import load_dotenv
from acitoolkit.acitoolkit import Session, Tenant

load_dotenv()


def get_session() -> Session:
    url  = os.getenv("APIC_URL")
    user = os.getenv("APIC_USER")
    pwd  = os.getenv("APIC_PASSWORD")

    session = Session(url, user, pwd, verify_ssl=False)
    response = session.login(timeout=10)

    if not response.ok:
        raise ConnectionError(f"Login failed: {response.text}")

    return session


def get_tenants(session: Session, limit: int = 15) -> list:
    tenants = Tenant.get(session)
    return tenants[:limit]


def display_tenants(tenants: list) -> None:
    print(f"\n{'#':<5} {'Name':<30} {'Description':<40}")
    print("-" * 75)

    for i, tenant in enumerate(tenants, start=1):
        print(f"{i:<5} {tenant.name:<30} {tenant.descr or '':<40}")


if __name__ == "__main__":
    try:
        session = get_session()
        tenants = get_tenants(session)
        display_tenants(tenants)

    except ConnectionError as e:
        print(f"Connection error: {e}")
        sys.exit(1)
