# WJC-NSCSW Collection - OCR Project Overview

**Collection:** Records of the National Security Council Speechwriting Office (Clinton Administration)
**Collection ID:** WJC-NSCSW
**NARA Collection naId:** 7388842
**Date Range:** 1993-2001 (Clinton presidency)
**Textual Records (Documents/Folders):** 2,053 file units
**Digital Objects (Total Pages):** 45,936 individual scanned pages/files
**Objects Without OCR:** ~43,842 (95.4%)
**OCR Rate:** 4.6% (very low - excellent gap for OCR project)
**Average Pages per Document:** 22.4 pages

---

## 📊 Collection Statistics

| Metric | Count |
|--------|-------|
| Total JSONL Files | 72 files |
| Total Metadata Size | 63.3 MB |
| **Textual Records (File Units)** | **2,053** |
| Records with Digital Objects | 2,053 (100%) |
| **Digital Objects (Total Pages)** | **45,936** |
| Objects with OCR | ~2,094 (4.6%) |
| **Objects WITHOUT OCR** | **~43,842 (95.4%)** |
| Average Pages per Record | 22.4 pages |

### Object Types (Individual Files)
- **JPG Images:** 43,884 (95.5%) - individual scanned pages
- **PDF Files:** 2,052 (4.5%) - born-digital or multi-page scans

### Document Size Distribution
- **1-10 pages:** 883 records (43.0%)
- **11-50 pages:** 909 records (44.3%)
- **51-100 pages:** 241 records (11.7%)
- **100+ pages:** 20 records (1.0%)

### Largest Documents (Selected Examples)
- **State of the Union - Ideas and Suggestions (1994):** 135 pages
- **State of the Union '98 - Drafts/Full Text:** 124 pages
- **UNGA Speech - Drafts - 10/22/95:** 120 pages
- **Bosnia - Oval Address:** 116 pages
- **Bosnia Statement 10/31/95:** 115 pages
- **State of Union Drafts 1/23/96:** 112 pages

---

## 🗂️ Collection Structure

### Hierarchy

```
Collection: Records of NSC Speechwriting Office (Clinton Administration)
└── naId: 7388842
    ├── Series: Antony Blinken's Files (1994-1998)
    │   └── naId: 7585787
    │   └── ~1,500+ file units
    │
    ├── Series: Robert Boorstin's Files (1994-1995)
    │   └── naId: 7585788
    │   └── ~200+ file units
    │
    ├── Series: Paul Orzulak's Files (1999-2001)
    │   └── naId: 7585791
    │   └── ~300+ file units
    │
    └── Series: Thomas Rosshirt's Files (2000-2001)
        └── naId: 7585792
        └── ~100+ file units
```

### Understanding Records vs Objects vs Pages

**IMPORTANT DISTINCTION:**

- **Records (File Units):** 2,053 distinct documents/folders
  - Example: "Bosnia Statement 10/31/95" = 1 record
  - Example: "Clinton - Fahd Press Statement" = 1 record

- **Digital Objects:** 45,936 individual files (JPGs and PDFs)
  - Each JPG = 1 scanned page
  - Each PDF = 1 file (may contain 1 or more pages)

- **Total Pages:** ~45,936 pages to OCR
  - "Bosnia Statement 10/31/95" = 1 record with **115 JPG objects** = **115 pages**
  - "Clinton - Fahd Press Statement" = 1 record with **5 JPG objects** = **5 pages**

**How Documents Are Stored:**
- Most multi-page documents are stored as **individual JPG files per page**, not combined PDFs
- Example: A 50-page speech will have 50 separate JPG files, each representing one page
- This is why we have 43,884 JPG files but only 2,053 records

### Key Personnel

**Antony Blinken** (1994-1998)
- Later served as:
  - Deputy Secretary of State (2015-2017, Obama administration)
  - **Secretary of State (2021-present, Biden administration)**
- Files cover critical mid-1990s foreign policy: Bosnia war, Middle East peace process, Russia relations, China policy

**Robert Boorstin** (1994-1995)
- Early Clinton administration speechwriting
- Shorter tenure, smaller collection

**Paul Orzulak** (1999-2001)
- Later Clinton administration (second term)
- Kosovo war, post-9/11 preparations, China relations

**Thomas Rosshirt** (2000-2001)
- Final year of Clinton presidency
- Transition period materials

---

## 📁 File Organization & Access

### S3 Bucket Structure

**Metadata Location:**
```
s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/
├── coll_WJC-NSCSW-1.jsonl
├── coll_WJC-NSCSW-2.jsonl
├── ...
└── coll_WJC-NSCSW-72.jsonl
```

**Digital Objects Location:**
Objects are hosted in two main S3 paths:

1. **FOIA Releases (JPG scans):**
   ```
   https://s3.amazonaws.com/NARAprodstorage/opastorage/live/{id1}/{id2}/{naId}/content/presidential-libraries/clinton/foia/{year}/{foia-number}/
   ```

   Example:
   ```
   https://s3.amazonaws.com/NARAprodstorage/opastorage/live/79/9029/23902979/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_03/42-t-7585787-20060459F-003-030-2016/42_t_7585787_20060459F_003_030_2016_Page_002.JPG
   ```

2. **Direct PDF Access:**
   ```
   https://s3.amazonaws.com/NARAprodstorage/lz/presidential-libraries/clinton/foia/{year}/{foia-number}/
   ```

   Example:
   ```
   https://s3.amazonaws.com/NARAprodstorage/lz/presidential-libraries/clinton/foia/2008/2008-0702-F/42-t-7585791-20080702f-002-009-2014.pdf
   ```

### Filename Conventions

**Pattern:** `42-t-{series_naId}-{foia_number}-{box}-{folder}-{year}.{ext}`

Example breakdown:
- `42-t-7585787-20060459F-003-030-2016.pdf`
  - `42` = Clinton Presidential Records code
  - `t` = Textual records
  - `7585787` = Series naId (Blinken's Files)
  - `20060459F` = FOIA request number (2006-0459-F)
  - `003-030` = Box 3, Folder 30
  - `2016` = Year processed/digitized

---

## 🌍 Content & Topics

### Major Themes

**Foreign Policy & International Relations** (Primary focus)
- **Bosnia Crisis (1994-1995):** Presidential addresses, press statements, diplomatic communications
- **Middle East:** US-Saudi relations, Iraq policy, Arab-Israeli peace process
- **Russia Relations:** Post-Cold War cooperation, arms control
- **China Policy:** Diplomatic visits, trade relations, human rights
- **Latin America:** Canada relations, Chile visits, hemispheric policy
- **Europe:** EU relations, Spain visits, NATO expansion

**Domestic Speeches & Addresses**
- Military academy commencements (Air Force Academy, Coast Guard Academy)
- Veterans Day events
- Domestic policy announcements
- Medal of Honor ceremonies

**Document Types**
- Presidential speech drafts (multiple revisions)
- Press availability statements
- State dinner toasts
- Diplomatic visit remarks
- Oval Office addresses
- Foreign policy briefings

### Geographic Coverage

Documents reference or relate to:
- **Middle East:** Saudi Arabia, Iraq, Kuwait, Israel
- **Europe:** Bosnia, Spain, Germany, UK, France
- **Asia:** China, Japan, Korea
- **Americas:** Canada, Chile, Mexico
- **Africa:** Various references in freedom/democracy speeches

---

## 🔐 Access Restrictions & Metadata Quality

### FOIA Restrictions

**Most Common Restrictions:**
- `FOIA (b)(1)` - National Security (classified information)
- `FOIA (b)(2)` - Internal Personnel Rules and Practices
- `FOIA (b)(6)` - Personal Information (privacy)
- `FOIA (b)(7)(c)` - Law Enforcement (personal privacy)
- `FOIA (b)(7)(e)` - Law Enforcement (techniques)

**Status:** Most records are "Restricted - Partly" meaning portions have been redacted/withheld

**Note:** Despite restrictions, substantial content has been released through FOIA. Redactions typically cover:
- Classified national security information
- Personal identifying information
- Internal deliberations
- Law enforcement sensitive information

### Metadata Quality

**Excellent metadata structure:**
- ✅ **Hierarchical Organization:** Collection → Series → File Unit → Item clearly defined
- ✅ **naId References:** Every level has unique National Archives Identifier
- ✅ **Date Information:** Inclusive start/end dates for series and collection
- ✅ **Creator Information:** Links to authority records for NSC offices
- ✅ **Access Status:** Clear indication of restrictions with specific FOIA exemptions cited
- ✅ **Physical Location:** References to William J. Clinton Presidential Library
- ✅ **FOIA Tracking:** Variant control numbers link to FOIA request numbers
- ✅ **Digital Object URLs:** Direct S3 links to every digitized page

**Metadata Fields Available:**
```json
{
  "naId": 23902979,
  "title": "Clinton - Fahd Press Statement",
  "levelOfDescription": "fileUnit",
  "generalRecordsTypes": ["Textual Records"],
  "accessRestriction": {
    "status": "Restricted - Partly",
    "note": "...",
    "specificAccessRestrictions": [...]
  },
  "ancestors": [...],
  "digitalObjects": [
    {
      "objectId": "55252342",
      "objectType": "Portable Document File (PDF)",
      "objectFilename": "...",
      "objectUrl": "https://...",
      "objectFileSize": 172556,
      "extractedText": "..." // RARELY present - this is the gap!
    }
  ],
  "physicalOccurrences": [...],
  "variantControlNumbers": [
    {"type": "FOIA Tracking Number", "number": "LPWJC 2006-0459-F"}
  ]
}
```

---

## 📋 CLI Access Guide

### Listing Collection Files

```bash
# List all metadata files
aws s3 ls s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/ --no-sign-request

# Output: 72 JSONL files (coll_WJC-NSCSW-1.jsonl through coll_WJC-NSCSW-72.jsonl)
```

### Downloading Metadata

```bash
# Download single file
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request 2>/dev/null

# Download all metadata files
aws s3 sync s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/ . --no-sign-request
```

### Sampling Records

```bash
# Get first 10 records from file 1
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request 2>/dev/null | head -10

# Random sample of 5 records
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request 2>/dev/null | python3 -c "
import json, sys, random
lines = [l for l in sys.stdin if l.strip()]
for line in random.sample(lines, min(5, len(lines))):
    record = json.loads(line)['record']
    print(f\"{record.get('naId')}: {record.get('title')}\")
"
```

### Finding Records by Series

```bash
# Find all Blinken files (naId 7585787)
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request 2>/dev/null | python3 -c "
import json, sys
for line in sys.stdin:
    record = json.loads(line.strip())['record']
    for anc in record.get('ancestors', []):
        if anc.get('naId') == 7585787:
            print(f\"{record.get('title')}\")
            break
"
```

### Downloading Digital Objects

```bash
# Download a specific image
curl -s "https://s3.amazonaws.com/NARAprodstorage/opastorage/live/79/9029/23902979/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_03/42-t-7585787-20060459F-003-030-2016/42_t_7585787_20060459F_003_030_2016_Page_002.JPG" -o clinton_fahd_statement.jpg

# Download a PDF
curl -s "https://s3.amazonaws.com/NARAprodstorage/lz/presidential-libraries/clinton/foia/2008/2008-0702-F/42-t-7585791-20080702f-002-009-2014.pdf" -o china_briefing.pdf
```

### Checking OCR Status

```bash
# Count records with/without OCR
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request 2>/dev/null | python3 -c "
import json, sys
with_ocr = 0
without_ocr = 0
for line in sys.stdin:
    record = json.loads(line.strip())['record']
    for obj in record.get('digitalObjects', []):
        if 'extractedText' in obj and len(obj.get('extractedText', '').strip()) > 10:
            with_ocr += 1
        else:
            without_ocr += 1
print(f'With OCR: {with_ocr}')
print(f'Without OCR: {without_ocr}')
print(f'OCR Rate: {with_ocr/(with_ocr+without_ocr)*100:.2f}%')
"
```

---

## 🔍 Content Examples with URLs

### Example 1: Clinton-Fahd Press Statement (Saudi Arabia Relations)

**Title:** Clinton - Fahd Press Statement
**naId:** 23902979
**Series:** Antony Blinken's Files
**Date:** October 1994
**Topic:** US-Saudi relations, Saddam Hussein crisis, Gulf security, Arab-Israeli peace process

**Content Preview:**
> "I confer frequently with King Fahd by phone and letter, but this was our first meeting. We had good discussions and further cemented the close relations which our two nations began fifty years ago when President Roosevelt met King Abdul-Aziz on the USS Quincy... This crisis, generated by Saddam Hussein's threatening moves and bellicose statements, has reinforced the importance of U.S.-Saudi cooperation."

**Digital Objects:**
- Page 1: https://s3.amazonaws.com/NARAprodstorage/opastorage/live/79/9029/23902979/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_03/42-t-7585787-20060459F-003-030-2016/42_t_7585787_20060459F_003_030_2016_Page_001.JPG
- Page 2 (State Draft): https://s3.amazonaws.com/NARAprodstorage/opastorage/live/79/9029/23902979/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_03/42-t-7585787-20060459F-003-030-2016/42_t_7585787_20060459F_003_030_2016_Page_002.JPG

**OCR Status:** No OCR
**Assessment:** ⭐⭐⭐⭐⭐ Typed English text, substantive foreign policy content

---

### Example 2: Bosnia Statement (Balkans Crisis)

**Title:** Bosnia Statement 10/31/95
**naId:** 23903206
**Series:** Antony Blinken's Files
**Date:** October 31, 1995
**Topic:** Bosnia war, Dayton peace negotiations, US intervention

**Digital Objects:** 115 pages (extensive drafts and revisions)
**OCR Status:** No OCR
**Assessment:** ⭐⭐⭐⭐⭐ Major foreign policy crisis, multiple speech drafts showing policy evolution

---

### Example 3: Air Force Academy Commencement Speech

**Title:** Air Force Academy - Drafts May 31, 1995 [1]
**naId:** 23903112
**Series:** Antony Blinken's Files
**Date:** May 31, 1995
**Topic:** Military leadership, national security, domestic address

**Metadata Preview:**
- Contains withdrawal/redaction sheet showing:
  - Document 001: "re: Air Force Academy Commencement" (13 pages), dated 05/30/1995, P5 restriction
  - Multiple duplicates with dates 05/30/1995 and 05/26/1995

**Digital Objects:**
- Marker page: https://s3.amazonaws.com/NARAprodstorage/opastorage/live/12/9031/23903112/content/presidential-libraries/clinton/foia/2006/2006-0459-F/2006-0459-F-JPG/Box_09/42-t-7585787-20060459F-009-017-2016/42_t_7585787_20060459F_009_017_2016_Page_001.JPG

**OCR Status:** No OCR
**Restrictions:** P5 (Presidential communications privilege)

---

### Example 4: China Policy Documents

**Title:** China [Folder 2] [7]
**naId:** 158702972
**Series:** Paul Orzulak's Files
**Date:** 1999-2001 (second Clinton term)
**Topic:** US-China relations, trade, human rights

**Digital Objects:** PDF format
**URL:** https://s3.amazonaws.com/NARAprodstorage/lz/presidential-libraries/clinton/foia/2008/2008-0702-F/42-t-7585791-20080702f-002-009-2014.pdf

**OCR Status:** No OCR
**Restrictions:** Top Secret (FOIA b(1) National Security), Personal Information (b(6))

---

### Example 5: Iraq & Haiti Oval Office Address

**Title:** Clinton - Iraq & Haiti, Oval Office 10/10/94
**naId:** 23902958
**Series:** Antony Blinken's Files
**Date:** October 10, 1994
**Topic:** Dual crises - Iraq military movements, Haiti intervention

**Digital Objects:** 11 pages
**OCR Status:** No OCR
**Assessment:** ⭐⭐⭐⭐⭐ Major presidential address addressing two simultaneous foreign policy crises

---

### Example 6: Canada Signing Ceremony

**Title:** Canada - Signing Ceremony 2/24/95
**naId:** 23903057
**Series:** Antony Blinken's Files
**Date:** February 24, 1995
**Topic:** US-Canada bilateral relations, treaty signing

**Digital Objects:** Multiple pages
**OCR Status:** No OCR

---

### Example 7: V.J. Day 50th Anniversary - Hawaii

**Title:** V.J. Day - Arrival - Hickam - August 31, 1995
**naId:** 23903145
**Series:** Antony Blinken's Files
**Date:** August 31, 1995
**Topic:** World War II commemoration, US-Japan relations, Pacific theater history

**Digital Objects:** 66 pages (extensive)
**OCR Status:** No OCR
**Assessment:** ⭐⭐⭐⭐ Historical commemoration with foreign policy dimensions

---

### Example 8: Lake CFR Speech (Council on Foreign Relations)

**Title:** Lake - CFR Speech - FINAL 9/12/94
**naId:** 23902918
**Series:** Antony Blinken's Files
**Date:** September 12, 1994
**Topic:** Anthony Lake (National Security Advisor) speech on foreign policy strategy

**Digital Objects:** 22 pages
**OCR Status:** No OCR
**Assessment:** ⭐⭐⭐⭐⭐ Major foreign policy address by National Security Advisor (Lake was Blinken's boss)

---

## 🎯 Why This Collection is Ideal for OCR

### 1. **Textual Richness** ✅
- **Speech drafts:** Full paragraphs of policy argumentation, not just data points
- **Historical narrative:** Documents tell stories about foreign policy decisions
- **Rhetorical content:** Presidential addresses designed to persuade and explain
- **Substantive analysis:** Policy briefings with context and reasoning

### 2. **OCR-Friendly Format** ✅
- **Typed documents:** Nearly all content is typewritten (pre-2001)
- **English language:** No translation required
- **Standard fonts:** Government/White House standard typewriter and word processor fonts
- **High-quality scans:** 300 DPI JPGs, clear and readable

### 3. **Historical Significance** ✅
- **Key decision-maker:** Antony Blinken is current Secretary of State (2021-present)
- **Major events:** Bosnia war, Middle East peace process, post-Cold War Russia
- **1990s foreign policy:** Critical decade between Cold War and 9/11
- **Presidential communications:** Direct insight into White House decision-making

### 4. **Research Value** ✅
**Potential user communities:**
- **Historians:** 1990s foreign policy, Clinton presidency, Balkans crisis
- **Political scientists:** Presidential rhetoric, foreign policy formation
- **International relations scholars:** US diplomacy, NATO expansion, Middle East policy
- **Journalists:** Context for current events (Blinken connection)
- **Students:** Primary sources for research papers on 1990s history

### 5. **Manageable Scale** ✅
- **2,053 records, 45,936 pages:** Substantial but achievable
- **Average 22 pages/document:** Reasonable workload per record
- **4 series:** Natural division for phased approach
- **Well-organized:** Clear hierarchy and metadata
- **Documented:** Excellent FOIA tracking and cataloging

### 6. **Partnership Potential** ✅
- **Clinton Presidential Library:** Direct stakeholder in Little Rock, AR
- **Academic institutions:** History departments studying 1990s foreign policy
- **Think tanks:** Brookings, CFR, CSIS interested in historical policy documents
- **Archives organizations:** National Archives, SAA, Digital Public Library of America

---

## 🚀 Recommended OCR Project Approach

### Phase 1: Proof of Concept (Blinken Bosnia Materials)
**Target:** Bosnia-related documents from Blinken series (1994-1995)
- ~50-100 records (documents)
- ~3,000-5,000 pages (estimated based on multi-page documents)
- Major historical event (Dayton Accords)
- Current Secretary of State's files
- **Timeline:** 2-4 weeks

### Phase 2: Blinken Series Complete (1994-1998)
**Target:** All Antony Blinken files
- ~1,500 records (documents)
- ~25,000-30,000 pages (estimated, majority of collection)
- Most historically significant series
- **Timeline:** 2-3 months

### Phase 3: Full Collection (1993-2001)
**Target:** All four series
- **2,053 records** (textual documents)
- **45,936 total pages** (JPG + PDF files)
- Complete NSC speechwriting archive
- **Timeline:** 4-6 months

### Processing Time Estimates

**Total workload:** ~45,936 pages to OCR

**OCR Processing Speed:**
- **Tesseract (CPU):** ~100-200 pages/hour = 230-460 hours (~10-19 days continuous)
- **Google Cloud Vision API:** ~500-1,000 pages/hour = 46-92 hours (~2-4 days)
- **Amazon Textract:** ~500-1,000 pages/hour = 46-92 hours (~2-4 days)

**With parallel processing (10 workers):**
- Tesseract: ~1-2 days
- Commercial APIs: ~5-10 hours

**Practical timeline (including review/QA):** 1-2 weeks for full collection

### Technology Stack Recommendations

**OCR Engine Options:**
1. **Tesseract 5.x** (open source)
   - Excellent for typed English text
   - Free, widely supported
   - Good for government documents

2. **Google Cloud Vision API** (commercial)
   - Higher accuracy on complex layouts
   - Handles redactions well
   - PDF and image support

3. **Amazon Textract** (commercial)
   - Good for government forms
   - Table extraction capabilities
   - AWS integration (same host as NARA data)

**Processing Pipeline:**
```
1. Download metadata JSONL files
2. Extract digitalObject URLs
3. Download images/PDFs from S3
4. Run OCR engine
5. Extract text + confidence scores
6. Store results with naId references
7. Create searchable database
8. Build web interface
```

---

## 📄 Sample Code: Full Collection Processing

```python
import json
import subprocess
import requests
from pathlib import Path

# Download all metadata
def download_metadata():
    for i in range(1, 73):  # 72 files
        subprocess.run([
            "aws", "s3", "cp",
            f"s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-{i}.jsonl",
            f"metadata/coll_WJC-NSCSW-{i}.jsonl",
            "--no-sign-request"
        ])

# Process records and extract object URLs
def extract_object_urls():
    urls = []
    for jsonl_file in Path("metadata").glob("*.jsonl"):
        with open(jsonl_file) as f:
            for line in f:
                record = json.loads(line)['record']
                na_id = record.get('naId')
                for obj in record.get('digitalObjects', []):
                    # Check if OCR already exists
                    has_ocr = 'extractedText' in obj and len(obj.get('extractedText', '').strip()) > 10
                    if not has_ocr:  # Only process objects without OCR
                        urls.append({
                            'naId': na_id,
                            'title': record.get('title'),
                            'url': obj.get('objectUrl'),
                            'filename': obj.get('objectFilename'),
                            'type': obj.get('objectType')
                        })
    return urls

# Download and OCR images
def process_objects(urls):
    for item in urls:
        # Download
        response = requests.get(item['url'])
        local_path = f"images/{item['naId']}_{item['filename']}"
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(response.content)

        # Run OCR (example with Tesseract)
        ocr_result = subprocess.run(
            ["tesseract", local_path, "stdout"],
            capture_output=True,
            text=True
        )

        # Save OCR text
        ocr_path = f"ocr_text/{item['naId']}_{item['filename']}.txt"
        Path(ocr_path).parent.mkdir(parents=True, exist_ok=True)
        with open(ocr_path, 'w') as f:
            f.write(ocr_result.stdout)

        print(f"Processed: {item['title']}")

# Main execution
if __name__ == "__main__":
    download_metadata()
    urls = extract_object_urls()
    print(f"Found {len(urls)} objects without OCR")
    process_objects(urls)
```

---

## 🏆 Expected Outcomes

### Immediate Impact
- **45,936 pages** made searchable for the first time (from 2,053 documents)
- Full-text search across 1990s NSC speechwriting files
- Citation-ready primary sources with naId references
- ~43,842 pages currently without OCR now accessible

### Research Applications
- **Bosnia war studies:** Searchable corpus of US policy documents
- **Middle East diplomacy:** Clinton-era peace process materials
- **Blinken biography:** Career trajectory from NSC speechwriter to Secretary of State
- **Presidential rhetoric:** Analysis of speech drafting and policy communication

### Partnership Opportunities
- **Clinton Library collaboration:** Official partnership with presidential library
- **Academic grants:** NEH, Mellon Foundation funding for digital humanities
- **Press coverage:** "Blinken's 1990s Files Now Searchable" angle
- **Policy community:** Think tank interest in historical foreign policy analysis

---

## 📚 Additional Resources

**Clinton Presidential Library:**
- Website: https://www.clintonlibrary.gov/
- Address: 1200 President Clinton Avenue, Little Rock, AR 72201
- Phone: 501-244-2877
- Email: clinton.library@nara.gov

**NARA Catalog:**
- Collection naId: 7388842
- https://catalog.archives.gov/id/7388842

**Related Collections:**
- WJC-NSCPC (NSC Press & Communications) - 12,614 objects, 6.9% OCR
- WJC-OS (Office of Speechwriting) - 227,178 objects, 4.5% OCR

**FOIA Requests:**
- Most documents released through FOIA requests 2006-2016
- Tracking numbers in metadata (LPWJC prefix)

---

## ✅ Project Decision Summary

**RECOMMENDED: Proceed with WJC-NSCSW as primary OCR project**

**Strengths:**
- ⭐⭐⭐⭐⭐ Textual richness (speeches, policy analysis, not just data)
- ⭐⭐⭐⭐⭐ OCR-friendly (typed English, high-quality scans)
- ⭐⭐⭐⭐⭐ Historical significance (current Secretary of State's files)
- ⭐⭐⭐⭐⭐ Research value (multiple academic communities)
- ⭐⭐⭐⭐ Manageable scale (40K objects)
- ⭐⭐⭐⭐⭐ Excellent metadata (naId, dates, FOIA tracking)

**Advantages over RG 82 (Federal Reserve Banking):**
- More narrative text vs. numerical data
- Broader research appeal (foreign policy > banking history)
- Contemporary relevance (Blinken connection)
- Better storytelling potential for outreach

**Next Steps:**
1. Download all 72 metadata files
2. Extract and catalog all ~43,842 non-OCR pages (from 45,936 total)
3. Select Bosnia subset for proof-of-concept (50-100 docs, ~3,000-5,000 pages)
4. Test OCR engines (Tesseract, Google Vision, AWS Textract)
5. Establish workflow and quality metrics
6. Scale to full collection (2,053 records, 45,936 pages)
