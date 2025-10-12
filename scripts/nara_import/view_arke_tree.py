#!/usr/bin/env python3
"""
View the Arke tree structure starting from the genesis block.
"""

from arke_api_client import ArkeClient

def view_tree():
    """Display the Arke tree hierarchy"""

    client = ArkeClient("http://localhost:8787")

    # Get Arke genesis block
    arke = client.get_arke_block()

    print("=== Arke Genesis Block Tree ===")
    print(f"Arke (PI: {arke['pi']}, v{arke['ver']})")
    print(f"└─ Note: {arke.get('note', 'N/A')}")
    print(f"└─ Children: {len(arke.get('children_pi', []))}")

    # Show institutions
    for inst_pi in arke.get('children_pi', []):
        print(f"\n  └─ Institution: {inst_pi}")

        try:
            inst = client.get_entity(inst_pi)
            print(f"     ├─ Version: v{inst['ver']}")
            print(f"     ├─ Note: {inst.get('note', 'N/A')}")
            print(f"     └─ Collections: {len(inst.get('children_pi', []))}")

            # Show first 3 collections
            for i, coll_pi in enumerate(inst.get('children_pi', [])[:3]):
                prefix = "        ├─" if i < min(2, len(inst.get('children_pi', [])) - 1) else "        └─"
                print(f"{prefix} Collection: {coll_pi}")

            if len(inst.get('children_pi', [])) > 3:
                print(f"        └─ ... and {len(inst.get('children_pi', [])) - 3} more collections")

        except Exception as e:
            print(f"     └─ Error: {e}")

    print("\n" + "="*50)

if __name__ == "__main__":
    view_tree()
