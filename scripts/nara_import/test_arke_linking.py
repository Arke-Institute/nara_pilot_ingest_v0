#!/usr/bin/env python3
"""
Test script to verify automatic linking of institutions to Arke genesis block.
"""

import sys
from arke_api_client import ArkeClient
from nara_importer import NARAImporter

def test_arke_linking():
    """Test that new institutions are automatically linked to Arke block"""

    # Initialize client
    client = ArkeClient("http://localhost:8787")

    # Get current Arke block state
    print("=== Before Creating Institution ===")
    arke_before = client.get_arke_block()
    print(f"Arke PI: {arke_before['pi']}")
    print(f"Arke version: {arke_before['ver']}")
    print(f"Current children: {arke_before.get('children_pi', [])}")
    print(f"Number of children: {len(arke_before.get('children_pi', []))}")

    # Create importer and test institution
    importer = NARAImporter(client, collection_id="TEST")

    print("\n=== Creating Test Institution ===")
    inst_pi = importer.import_institution(
        name="Test Library",
        description="Test library for Arke linking validation",
        url="https://test-library.example.com"
    )
    print(f"Created institution: {inst_pi}")

    # Get updated Arke block state
    print("\n=== After Creating Institution ===")
    arke_after = client.get_arke_block()
    print(f"Arke PI: {arke_after['pi']}")
    print(f"Arke version: {arke_after['ver']}")
    print(f"Current children: {arke_after.get('children_pi', [])}")
    print(f"Number of children: {len(arke_after.get('children_pi', []))}")

    # Verify institution was added
    if inst_pi in arke_after.get('children_pi', []):
        print(f"\n✅ SUCCESS: Institution {inst_pi} is linked to Arke block!")
        return True
    else:
        print(f"\n❌ FAILURE: Institution {inst_pi} is NOT linked to Arke block")
        return False

if __name__ == "__main__":
    try:
        success = test_arke_linking()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
