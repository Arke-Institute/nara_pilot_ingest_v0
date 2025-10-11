# NARA Collection Importer for Arke IPFS

This toolkit imports NARA (National Archives) collections into the Arke IPFS database using a hierarchical entity structure.

## Overview

The importer creates a four-level hierarchy:

```
Collection (e.g., WJC-NSCSW)
└── Series (e.g., Antony Blinken's Files)
    └── FileUnit (e.g., "Clinton - Address on Haiti 9/15/94")
        └── DigitalObject (e.g., Page 1, Page 2, ...)
```

Each level is represented as an Arke entity with:
- **Unique PI** (Persistent Identifier) using ULID
- **Catalog metadata** stored in IPFS
- **Parent-child relationships** via `children_pi` arrays

## Key Design Decisions

### 1. **No Image Storage in IPFS**
- Digital objects (JPGs/PDFs) are **NOT** uploaded to IPFS
- Instead, we store:
  - S3 URL (original location)
  - SHA256 hash (content verification)
  - Metadata (filename, size, type, etc.)

**Rationale**: The full collection is ~46K images. Storing S3 URLs + hashes is lightweight and allows future OCR without re-downloading.

### 2. **Hierarchical PI Naming**

Format: `NARA-<COLLECTION_ID>-<TYPE>-<NARA_ID>-<ULID>`

Examples:
```
NARA-WJC-NSCSW-COL-7388842-01JABBCCDDEEFFGGHHKKMMNNPP     (Collection)
NARA-WJC-NSCSW-SER-7585787-01JABBCCDDEEFFGGHHKKMMNNPP     (Series)
NARA-WJC-NSCSW-FILE-23902919-01JABBCCDDEEFFGGHHKKMMNNPP   (FileUnit)
NARA-WJC-NSCSW-OBJ-55251313-01JABBCCDDEEFFGGHHKKMMNNPP    (DigitalObject)
```

**Benefits**:
- Human-readable
- Includes NARA identifiers for traceability
- ULID ensures uniqueness and sortability
- Type prefix allows filtering by entity type

### 3. **Streaming Hash Computation**

Digital objects are hashed using streaming downloads:
1. Download file in 8KB chunks
2. Compute SHA256 on-the-fly
3. Discard bytes immediately
4. Store only the hash digest

**Benefits**:
- Minimal memory usage (~8KB per file)
- No local disk storage required
- Can process thousands of files without filling disk

## File Structure

```
nara_import/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── nara_schema.py               # Catalog record schemas
├── nara_pi.py                   # PI generation utilities
├── nara_hash_utils.py           # Hash computation utilities
├── arke_api_client.py           # Arke API client
├── nara_importer.py             # Main importer class
└── test_import_sample.py        # Test script (3-record sample)
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or manually:
pip install requests python-ulid
```

## Usage

### 1. Start Arke API

Ensure the Arke IPFS API is running:

```bash
# Example (adjust for your setup)
cd /path/to/arke-api
npm run dev  # or appropriate start command
```

Verify it's running:
```bash
curl http://localhost:8787
# Should return: {"service":"arke-ipfs-api","version":"0.1.0","status":"ok"}
```

### 2. Run Test Import

Import 3 sample records:

```bash
cd scripts/nara_import
python test_import_sample.py
```

**What it does**:
1. Downloads 3 records from NARA S3 bucket
2. Creates Collection entity (WJC-NSCSW)
3. Creates Series entity (e.g., Antony Blinken's Files)
4. Creates 3 FileUnit entities
5. Creates ~10-60 DigitalObject entities per FileUnit
6. Hashes all digital objects (without storing images)
7. Links hierarchy via `children_pi` relationships

**Expected output**:
```
=== NARA Import Test ===
API: http://localhost:8787
Collection: WJC-NSCSW
Records: 3
Dry run: False
========================================

1. Checking API health...
API Status: {'service': 'arke-ipfs-api', 'version': '0.1.0', 'status': 'ok'}

2. Downloading 3 sample records...
Sample records:
  1. [Coast Guard Academy] [Folder 2] [4] (naId: 158703016, 1 objects)
  2. Clinton - Address on Haiti 9/15/94 (naId: 23902919, 11 objects)
  3. [Japan, Germany, and Kosovo] [2] (naId: 158703044, 1 objects)

3. Initializing importer...

4. Importing 3 records...

--- Record 1/3: [Coast Guard Academy] [Folder 2] [4] ---
✓ Imported: NARA-WJC-NSCSW-FILE-158703016-01JAB...

...

=== Import Statistics ===
Collections created: 1
Series created:      1
FileUnits created:   3
DigitalObjects:      13
Bytes hashed:        8,234,567
Errors:              0
========================
```

### 3. Verify Import

Query the API to verify entities were created:

```bash
# List all entities
curl http://localhost:8787/entities?limit=10

# Get specific entity
curl http://localhost:8787/entities/NARA-WJC-NSCSW-COL-7388842-01JAB...

# Resolve PI to current tip
curl http://localhost:8787/resolve/NARA-WJC-NSCSW-FILE-23902919-01JAB...
```

## Catalog Record Schemas

### Collection Catalog Record
```json
{
  "schema": "nara-collection@v1",
  "nara_naId": 7388842,
  "collection_identifier": "WJC-NSCSW",
  "title": "Records of NSC Speechwriting Office (Clinton)",
  "date_range": {"start": "1993-01-01", "end": "2001-12-31"},
  "import_timestamp": "2025-10-10T19:43:15Z"
}
```

### Series Catalog Record
```json
{
  "schema": "nara-series@v1",
  "nara_naId": 7585787,
  "parent_naId": 7388842,
  "title": "Antony Blinken's Files",
  "date_range": {"start": "1994-01-01", "end": "1998-12-31"},
  "creators": [...],
  "import_timestamp": "2025-10-10T19:43:15Z"
}
```

### FileUnit Catalog Record
```json
{
  "schema": "nara-fileunit@v1",
  "nara_naId": 23902919,
  "parent_naId": 7585787,
  "collection_naId": 7388842,
  "title": "Clinton - Address on Haiti 9/15/94",
  "level": "fileUnit",
  "record_types": ["Textual Records"],
  "digital_object_count": 11,
  "foia_tracking": "LPWJC 2006-0459-F",
  "access_restriction": {...},
  "import_timestamp": "2025-10-10T19:43:15Z"
}
```

### DigitalObject Catalog Record
```json
{
  "schema": "nara-digitalobject@v1",
  "nara_objectId": "55251313",
  "parent_naId": 23902919,
  "filename": "42_t_7585787_20060459F_002_001_2016_Page_001.JPG",
  "object_type": "Image (JPG)",
  "file_size": 401408,
  "s3_url": "https://s3.amazonaws.com/NARAprodstorage/...",
  "content_hash": {
    "algorithm": "sha256",
    "digest_hex": "a3f58b4c..."
  },
  "page_number": 1,
  "extracted_text": null,
  "import_timestamp": "2025-10-10T19:43:15Z"
}
```

## Scaling to Full Collection

The test script imports 3 records (~13 pages). To import the full collection (2,053 records, 45,936 pages):

### Option 1: Process All JSONL Files
```python
# Create a full import script
import subprocess

for i in range(1, 73):  # 72 JSONL files
    cmd = [
        "aws", "s3", "cp",
        f"s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-{i}.jsonl",
        "-",
        "--no-sign-request"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    for line in result.stdout.strip().split("\n"):
        record = json.loads(line)["record"]
        import_record(importer, record)
```

### Option 2: Batch Processing

Process in batches to handle errors gracefully:

```python
# Import in batches of 100 records
for batch_start in range(0, 2053, 100):
    batch_end = min(batch_start + 100, 2053)
    print(f"Processing records {batch_start}-{batch_end}...")
    # Process batch
    # Save checkpoint
```

### Estimated Processing Time

For 45,936 digital objects:

| Component | Time |
|-----------|------|
| Hashing (parallel, 10 workers) | ~2-4 hours |
| IPFS uploads (metadata only) | ~1-2 hours |
| Entity creation | ~1-2 hours |
| **Total** | **~4-8 hours** |

## Troubleshooting

### API Connection Errors
```
ArkeAPIError: Request failed: Connection refused
```
**Solution**: Ensure Arke API is running at `http://localhost:8787`

### Hash Computation Errors
```
HashComputationError: Download failed: 404
```
**Solution**: S3 URL may be invalid or file deleted. Check NARA metadata.

### Conflict Errors
```
ArkeConflictError: Conflict: PI already exists
```
**Solution**: Entity already imported. Script will skip and continue.

## Next Steps

1. **Run test import** with 3 records
2. **Verify entities** in Arke API
3. **Scale to larger sample** (e.g., 50 records)
4. **Implement error recovery** (checkpoint/resume)
5. **Full collection import** (2,053 records)
6. **OCR integration** (future phase)

## Questions?

See main project documentation or contact the development team.
