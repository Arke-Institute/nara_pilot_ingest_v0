#!/usr/bin/env python3
"""
Generate Example NARA Import Structure

Creates local JSON files showing what the complete hierarchy looks like
WITHOUT uploading to the API. This is for demonstration/inspection only.
"""

import json
from pathlib import Path
from datetime import datetime

# Use fixed ULIDs for reproducibility (pre-generated)
COLLECTION_ULID = "01JCAQ8M5K2N3P4Q5R6S7T8V9W"
SERIES_ULID = "01JCAQ8N6L3M4P5Q6R7S8T9V0W"
FILEUNIT_ULID = "01JCAQ8P7M4N5P6Q7R8S9T0V1W"
OBJ_ULIDS = [
    "01JCAQ8Q8N5M6P7Q8R9S0T1V2W",
    "01JCAQ8R9P6N7P8Q9R0S1T2V3W",
    "01JCAQ8S0Q7M8P9Q0R1S2T3V4W",
    "01JCAQ8T1R8N9P0Q1R2S3T4V5W",
    "01JCAQ8V2S9M0P1Q2R3S4T5V6W",
    "01JCAQ8W3T0N1P2Q3R4S5T6V7W",
    "01JCAQ8X4V1M2P3Q4R5S6T7V8W",
    "01JCAQ8Y5W2N3P4Q5R6S7T8V9W",
    "01JCAQ8Z6X3M4P5Q6R7S8T9V0W",
    "01JCAQB07Y4N5P6Q7R8S9T0V1W",
    "01JCAQB18Z5M6P7Q8R9S0T1V2W",  # PDF
]

def generate_example():
    """Generate complete example structure locally"""

    base_dir = Path("example_structure")
    base_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (base_dir / "catalog_records" / "collection").mkdir(parents=True, exist_ok=True)
    (base_dir / "catalog_records" / "series").mkdir(parents=True, exist_ok=True)
    (base_dir / "catalog_records" / "fileunit").mkdir(parents=True, exist_ok=True)
    (base_dir / "catalog_records" / "digitalobject").mkdir(parents=True, exist_ok=True)

    (base_dir / "entity_manifests" / "collection").mkdir(parents=True, exist_ok=True)
    (base_dir / "entity_manifests" / "series").mkdir(parents=True, exist_ok=True)
    (base_dir / "entity_manifests" / "fileunit").mkdir(parents=True, exist_ok=True)
    (base_dir / "entity_manifests" / "digitalobject").mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().isoformat() + "Z"

    # ======================
    # 1. COLLECTION
    # ======================

    collection_pi = f"NARA-WJC-NSCSW-COL-7388842-{COLLECTION_ULID}"

    # Collection catalog record
    collection_catalog = {
        "schema": "nara-collection@v1",
        "nara_naId": 7388842,
        "collection_identifier": "WJC-NSCSW",
        "title": "Records of the National Security Council Speechwriting Office (Clinton Administration)",
        "date_range": {
            "start": "1993-01-01",
            "end": "2001-12-31"
        },
        "stats": {
            "total_series": 4,
            "total_file_units": 2053,
            "total_digital_objects": 45936
        },
        "import_timestamp": timestamp
    }

    # Save collection catalog
    with open(base_dir / "catalog_records" / "collection" / f"{collection_pi}.json", "w") as f:
        json.dump(collection_catalog, f, indent=2, sort_keys=True)

    # Collection manifest v1 (no children yet)
    collection_manifest_v1 = {
        "schema": "arke/manifest@v1",
        "pi": collection_pi,
        "ver": 1,
        "ts": timestamp,
        "prev": None,
        "components": {
            "catalog_record": {"/": "bafybeicol456ghi..."}
        },
        "children_pi": [],
        "note": "Collection: Records of the National Security Council Speechwriting Office (Clinton Administration) - naId:7388842"
    }

    # Collection manifest v2 (with series children)
    series_pi = f"NARA-WJC-NSCSW-SER-7585787-{SERIES_ULID}"

    collection_manifest_v2 = {
        "schema": "arke/manifest@v1",
        "pi": collection_pi,
        "ver": 2,
        "ts": timestamp,
        "prev": {"/": "bafybeiprev123..."},
        "components": {
            "catalog_record": {"/": "bafybeicol456ghi..."}
        },
        "children_pi": [
            series_pi,
            f"NARA-WJC-NSCSW-SER-7585788-01JCAQ8N7M3N4P5Q6R7S8T9V0W",
            f"NARA-WJC-NSCSW-SER-7585791-01JCAQ8N8N4M5P6Q7R8S9T0V1W",
            f"NARA-WJC-NSCSW-SER-7585792-01JCAQ8N9P5N6P7Q8R9S0T1V2W"
        ],
        "note": "Added 4 series"
    }

    # Save collection manifests
    col_manifest_dir = base_dir / "entity_manifests" / "collection" / collection_pi
    col_manifest_dir.mkdir(exist_ok=True)

    with open(col_manifest_dir / "v1.json", "w") as f:
        json.dump(collection_manifest_v1, f, indent=2, sort_keys=True)

    with open(col_manifest_dir / "v2.json", "w") as f:
        json.dump(collection_manifest_v2, f, indent=2, sort_keys=True)

    # ======================
    # 2. SERIES
    # ======================

    # Series catalog record
    series_catalog = {
        "schema": "nara-series@v1",
        "nara_naId": 7585787,
        "parent_naId": 7388842,
        "title": "Antony Blinken's Files",
        "date_range": {
            "start": "1994-01-01",
            "end": "1998-12-31"
        },
        "creators": [
            {
                "authorityType": "organization",
                "creatorType": "Most Recent",
                "heading": "President (1993-2001 : Clinton). National Security Council. (1993 - 2001)",
                "naId": 10500730,
                "establishDate": {
                    "logicalDate": "1993-01-01",
                    "year": 1993
                },
                "abolishDate": {
                    "logicalDate": "2001-12-31",
                    "year": 2001
                }
            }
        ],
        "import_timestamp": timestamp
    }

    with open(base_dir / "catalog_records" / "series" / f"{series_pi}.json", "w") as f:
        json.dump(series_catalog, f, indent=2, sort_keys=True)

    # Series manifests
    fileunit_pi = f"NARA-WJC-NSCSW-FILE-23902919-{FILEUNIT_ULID}"

    series_manifest_v1 = {
        "schema": "arke/manifest@v1",
        "pi": series_pi,
        "ver": 1,
        "ts": timestamp,
        "prev": None,
        "components": {
            "catalog_record": {"/": "bafybeiser123mno..."}
        },
        "children_pi": [],
        "note": "Series: Antony Blinken's Files - naId:7585787"
    }

    series_manifest_v2 = {
        "schema": "arke/manifest@v1",
        "pi": series_pi,
        "ver": 2,
        "ts": timestamp,
        "prev": {"/": "bafybeiprev456..."},
        "components": {
            "catalog_record": {"/": "bafybeiser123mno..."}
        },
        "children_pi": [
            fileunit_pi,
            "NARA-WJC-NSCSW-FILE-23902930-01JCAQ8P8N5M6P7Q8R9S0T1V2W",
            "... (about 1,500 fileunit PIs for Blinken series)"
        ],
        "note": "Added fileunits"
    }

    ser_manifest_dir = base_dir / "entity_manifests" / "series" / series_pi
    ser_manifest_dir.mkdir(exist_ok=True)

    with open(ser_manifest_dir / "v1.json", "w") as f:
        json.dump(series_manifest_v1, f, indent=2, sort_keys=True)

    with open(ser_manifest_dir / "v2.json", "w") as f:
        json.dump(series_manifest_v2, f, indent=2, sort_keys=True)

    # ======================
    # 3. FILEUNIT
    # ======================

    # FileUnit catalog record
    fileunit_catalog = {
        "schema": "nara-fileunit@v1",
        "nara_naId": 23902919,
        "parent_naId": 7585787,
        "collection_naId": 7388842,
        "title": "Clinton - Address on Haiti 9/15/94",
        "level": "fileUnit",
        "record_types": ["Textual Records"],
        "digital_object_count": 11,
        "foia_tracking": "LPWJC 2006-0459-F",
        "access_restriction": {
            "status": "Restricted - Partly",
            "note": "These records may need to be screened for personal privacy, and law enforcement under 5 U.S.C. 552 (b) prior to public release.",
            "specificAccessRestrictions": [
                {
                    "restriction": "FOIA (b)(1) National Security",
                    "securityClassification": "Secret"
                },
                {
                    "restriction": "FOIA (b)(6) Personal Information"
                }
            ]
        },
        "physical_location": {
            "copyStatus": "Preservation-Reproduction-Reference",
            "referenceUnit": {
                "name": "William J. Clinton Library",
                "address1": "1200 President Clinton Avenue",
                "city": "Little Rock",
                "state": "AR",
                "postalCode": "72201",
                "phone": "501-244-2877",
                "email": "clinton.library@nara.gov"
            }
        },
        "other_titles": ["42-t-7585787-20060459F-002-001-2014"],
        "import_timestamp": timestamp
    }

    with open(base_dir / "catalog_records" / "fileunit" / f"{fileunit_pi}.json", "w") as f:
        json.dump(fileunit_catalog, f, indent=2, sort_keys=True)

    # FileUnit manifests
    digitalobject_pis = [f"NARA-WJC-NSCSW-OBJ-{55251313 + i}-{OBJ_ULIDS[i]}" for i in range(11)]

    fileunit_manifest_v1 = {
        "schema": "arke/manifest@v1",
        "pi": fileunit_pi,
        "ver": 1,
        "ts": timestamp,
        "prev": None,
        "components": {
            "catalog_record": {"/": "bafybeifile456stu..."}
        },
        "children_pi": [],
        "note": "FileUnit: Clinton - Address on Haiti 9/15/94 - naId:23902919 (11 pages)"
    }

    fileunit_manifest_v2 = {
        "schema": "arke/manifest@v1",
        "pi": fileunit_pi,
        "ver": 2,
        "ts": timestamp,
        "prev": {"/": "bafybeiprev789..."},
        "components": {
            "catalog_record": {"/": "bafybeifile456stu..."}
        },
        "children_pi": digitalobject_pis,
        "note": "Added 11 digital objects"
    }

    file_manifest_dir = base_dir / "entity_manifests" / "fileunit" / fileunit_pi
    file_manifest_dir.mkdir(exist_ok=True)

    with open(file_manifest_dir / "v1.json", "w") as f:
        json.dump(fileunit_manifest_v1, f, indent=2, sort_keys=True)

    with open(file_manifest_dir / "v2.json", "w") as f:
        json.dump(fileunit_manifest_v2, f, indent=2, sort_keys=True)

    # ======================
    # 4. DIGITAL OBJECTS
    # ======================

    # Sample digital objects (with valid SHA256 hashes)
    digital_objects_data = [
        {
            "objectId": "55251313",
            "filename": "42_t_7585787_20060459F_002_001_2016_Page_001.JPG",
            "type": "Image (JPG)",
            "size": 401408,
            "page": 1,
            "hash": "a3f58b4c72e1d9f0a2b6c8e4d1f3a5b7c9e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0"
        },
        {
            "objectId": "55251314",
            "filename": "42_t_7585787_20060459F_002_001_2016_Page_002.JPG",
            "type": "Image (JPG)",
            "size": 540672,
            "page": 2,
            "hash": "b4f69c5d83f2e0a1b3c7d9f5e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f1"
        },
        {
            "objectId": "55251315",
            "filename": "42_t_7585787_20060459F_002_001_2016_Page_003.JPG",
            "type": "Image (JPG)",
            "size": 688128,
            "page": 3,
            "hash": "c5e70d6e94e3f1b2c4d8e0f6e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f2"
        },
    ]

    # Add remaining pages (4-10) with valid SHA256 hashes
    for i in range(4, 11):
        # Generate a valid 64-char hex string
        import hashlib
        seed = f"page_{i}_example".encode()
        hash_val = hashlib.sha256(seed).hexdigest()

        digital_objects_data.append({
            "objectId": f"{55251313 + i - 1}",
            "filename": f"42_t_7585787_20060459F_002_001_2016_Page_{i:03d}.JPG",
            "type": "Image (JPG)",
            "size": 600000 + i * 1000,
            "page": i,
            "hash": hash_val
        })

    # Add PDF (page 11)
    import hashlib
    pdf_hash = hashlib.sha256(b"pdf_example_with_ocr").hexdigest()

    digital_objects_data.append({
        "objectId": "55251312",
        "filename": "42-t-7585787-20060459F-002-001-2014.pdf",
        "type": "Portable Document File (PDF)",
        "size": 672372,
        "page": 11,
        "hash": pdf_hash,
        "ocr": "\\nCase Number: 2006-0459-F\\nFOIA\\nMARKER\\n...\\n\\nGood evening.\\n\\nMy fellow Americans, tonight I want to speak to you about why the United States is leading the international effort to restore democratic government in Haiti...\\n\\n[Full speech text - truncated for brevity]"
    })

    # Generate digital object records
    for i, obj_data in enumerate(digital_objects_data):
        obj_pi = digitalobject_pis[i]

        # Catalog record
        obj_catalog = {
            "schema": "nara-digitalobject@v1",
            "nara_objectId": obj_data["objectId"],
            "parent_naId": 23902919,
            "filename": obj_data["filename"],
            "object_type": obj_data["type"],
            "file_size": obj_data["size"],
            "s3_url": f"https://s3.amazonaws.com/NARAprodstorage/opastorage/live/19/9029/23902919/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_02/42-t-7585787-20060459F-002-001-2016/{obj_data['filename']}",
            "content_hash": {
                "algorithm": "sha256",
                "digest_hex": obj_data["hash"]
            },
            "page_number": obj_data["page"],
            "extracted_text": obj_data.get("ocr"),
            "import_timestamp": timestamp
        }

        with open(base_dir / "catalog_records" / "digitalobject" / f"{obj_pi}.json", "w") as f:
            json.dump(obj_catalog, f, indent=2, sort_keys=True)

        # Manifest (v1 only, no children)
        obj_manifest = {
            "schema": "arke/manifest@v1",
            "pi": obj_pi,
            "ver": 1,
            "ts": timestamp,
            "prev": None,
            "components": {
                "digital_object_metadata": {"/": f"bafybeiobj{i:03d}..."}
            },
            "children_pi": [],
            "note": f"Page {obj_data['page']}: {obj_data['filename']} - objectId:{obj_data['objectId']}"
        }

        obj_manifest_dir = base_dir / "entity_manifests" / "digitalobject" / obj_pi
        obj_manifest_dir.mkdir(exist_ok=True)

        with open(obj_manifest_dir / "v1.json", "w") as f:
            json.dump(obj_manifest, f, indent=2, sort_keys=True)

    # ======================
    # SUMMARY
    # ======================

    summary = {
        "collection": {
            "pi": collection_pi,
            "naId": 7388842,
            "title": "Records of NSC Speechwriting Office (Clinton)",
            "versions": 2,
            "children": 4
        },
        "series": {
            "pi": series_pi,
            "naId": 7585787,
            "title": "Antony Blinken's Files",
            "versions": 2,
            "children": "~1500 (shown: 1)"
        },
        "fileunit": {
            "pi": fileunit_pi,
            "naId": 23902919,
            "title": "Clinton - Address on Haiti 9/15/94",
            "versions": 2,
            "children": 11
        },
        "digitalobjects": {
            "count": 11,
            "types": {
                "JPG": 10,
                "PDF": 1
            },
            "total_size_bytes": sum(obj["size"] for obj in digital_objects_data),
            "with_ocr": 1
        },
        "storage": {
            "ipfs_storage_kb": "~30-50 KB (metadata only)",
            "actual_images_storage": "0 bytes (S3 URLs only)",
            "download_bandwidth_for_hashing_mb": "~6 MB"
        }
    }

    with open(base_dir / "SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    # ======================
    # RELATIONSHIP MAP
    # ======================

    relationship_map = {
        "hierarchy": {
            collection_pi: {
                "type": "collection",
                "children": {
                    series_pi: {
                        "type": "series",
                        "children": {
                            fileunit_pi: {
                                "type": "fileunit",
                                "children": {
                                    obj_pi: {"type": "digitalobject"}
                                    for obj_pi in digitalobject_pis
                                }
                            }
                        }
                    }
                }
            }
        },
        "reverse_lookup": {
            "digitalobject_to_fileunit": {obj_pi: fileunit_pi for obj_pi in digitalobject_pis},
            "fileunit_to_series": {fileunit_pi: series_pi},
            "series_to_collection": {series_pi: collection_pi}
        }
    }

    with open(base_dir / "RELATIONSHIPS.json", "w") as f:
        json.dump(relationship_map, f, indent=2, sort_keys=True)

    print("✓ Generated example structure in:", base_dir.absolute())
    print("\nStructure:")
    print(f"  Collection:      {collection_pi}")
    print(f"  └─ Series:       {series_pi}")
    print(f"     └─ FileUnit:  {fileunit_pi}")
    print(f"        └─ DigitalObjects: {len(digitalobject_pis)} objects")
    print("\nFiles created:")
    print(f"  Catalog records: {4 + 11} files")
    print(f"  Manifests:       {2 + 2 + 2 + 11} files (versions)")
    print(f"  Summary:         SUMMARY.json")
    print(f"  Relationships:   RELATIONSHIPS.json")


if __name__ == "__main__":
    generate_example()
