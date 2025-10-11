# WJC-NSCSW Collection - Exact Numbers Summary

**Last Updated:** October 6, 2025
**Data Source:** Complete analysis of all 72 JSONL metadata files

---

## 📊 Core Statistics

| Category | Count | Notes |
|----------|-------|-------|
| **Textual Records (File Units)** | **2,053** | Distinct documents/folders |
| **Digital Objects (Total)** | **45,936** | Individual scanned pages/files |
| **Average Pages per Record** | **22.4** | Calculated: 45,936 ÷ 2,053 |
| **Objects WITHOUT OCR** | **~43,842** | 95.4% of total |
| **Objects WITH OCR** | **~2,094** | 4.6% of total |

---

## 📄 Understanding the Numbers

### What is a "Record"?
- A **record** (file unit) = 1 document or folder in the collection
- Examples:
  - "Bosnia Statement 10/31/95" = 1 record
  - "Clinton - Fahd Press Statement" = 1 record
  - "State of the Union '98 - Drafts/Full Text" = 1 record

**Total records:** 2,053

### What is a "Digital Object"?
- A **digital object** = 1 individual file (JPG image or PDF)
- For multi-page documents, each page is stored as a separate JPG file
- Examples:
  - "Bosnia Statement 10/31/95" = 1 record containing **115 JPG files** (one per page)
  - "Clinton - Fahd Press Statement" = 1 record containing **5 JPG files**
  - Most documents are 10-50 pages long

**Total digital objects:** 45,936

### What is a "Page"?
- A **page** = 1 page of text to OCR
- Each JPG = 1 page
- Each PDF = typically 1 page (some may be multi-page)

**Total pages to OCR:** ~45,936 pages

---

## 🗂️ Object Type Breakdown

| Type | Count | Percentage | Notes |
|------|-------|------------|-------|
| **JPG Images** | **43,884** | **95.5%** | Individual scanned pages |
| **PDF Files** | **2,052** | **4.5%** | Born-digital or combined scans |
| **TOTAL** | **45,936** | **100%** | All digital objects |

---

## 📏 Document Size Distribution

| Page Range | Records | Percentage | Example Documents |
|------------|---------|------------|-------------------|
| **1-10 pages** | 883 | 43.0% | Brief statements, press releases |
| **11-50 pages** | 909 | 44.3% | Standard speeches, policy memos |
| **51-100 pages** | 241 | 11.7% | Major addresses with drafts |
| **100+ pages** | 20 | 1.0% | State of Union, Bosnia crisis docs |
| **TOTAL** | **2,053** | **100%** | All records |

---

## 📚 Largest Documents (100+ Pages)

| Rank | Document Title | Pages |
|------|----------------|-------|
| 1 | State of the Union - Ideas and Suggestions (1994) | 135 |
| 2 | State of the Union '98 - Drafts/Full Text | 124 |
| 3 | UNGA Speech - Drafts - 10/22/95 [2] | 120 |
| 4 | Bosnia - Oval Address [1] | 116 |
| 5 | Bosnia Statement 10/31/95 | 115 |
| 6 | State of Union Drafts 1/23/96 | 112 |
| 7 | Lake - Princeton Speech - Notes [1] | 110 |
| 8 | Bosnia - Oval Address [2] | 109 |
| 9 | Lake - Intel Speech Background 3/95 [1] | 109 |
| 10 | SRB Iraq Speech 2/13/98 | 108 |

*Complete list of 20 documents with 100+ pages available in detailed analysis*

---

## 🎯 OCR Project Scope

### Pages Requiring OCR
- **Total pages:** 45,936
- **Pages without OCR:** ~43,842 (95.4%)
- **Pages with OCR:** ~2,094 (4.6%)

### Workload Breakdown by Series

| Series | Estimated Records | Estimated Pages | Date Range |
|--------|------------------|-----------------|------------|
| Antony Blinken's Files | ~1,500 | ~25,000-30,000 | 1994-1998 |
| Robert Boorstin's Files | ~200 | ~3,000-5,000 | 1994-1995 |
| Paul Orzulak's Files | ~300 | ~10,000-12,000 | 1999-2001 |
| Thomas Rosshirt's Files | ~100 | ~3,000-4,000 | 2000-2001 |
| **TOTAL** | **~2,053** | **~45,936** | 1993-2001 |

---

## ⏱️ Processing Time Estimates

### OCR Engine Performance (45,936 pages)

**Single Worker:**
| Engine | Pages/Hour | Total Hours | Total Days |
|--------|-----------|-------------|------------|
| Tesseract (CPU) | 100-200 | 230-460 | 10-19 days |
| Google Cloud Vision | 500-1,000 | 46-92 | 2-4 days |
| Amazon Textract | 500-1,000 | 46-92 | 2-4 days |

**Parallel Processing (10 workers):**
| Engine | Total Time |
|--------|-----------|
| Tesseract | 1-2 days |
| Google Cloud Vision | 5-10 hours |
| Amazon Textract | 5-10 hours |

**Practical Timeline (including QA/review):** 1-2 weeks for full collection

---

## 🔢 How We Got These Numbers

### Methodology
1. Downloaded and analyzed all 72 JSONL metadata files
2. Counted records where `levelOfDescription == "fileUnit"`
3. Counted all `digitalObjects` arrays across all records
4. Categorized by `objectType` field
5. Measured `digitalObjects` length for each record to determine page distribution

### Data Collection Date
- **Analysis performed:** October 6, 2025
- **Source:** `s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/`
- **Files analyzed:** All 72 JSONL files (coll_WJC-NSCSW-1.jsonl through coll_WJC-NSCSW-72.jsonl)

### Verification
- Cross-checked against overnight discovery results
- Overnight results showed 40,978 objects (sample-based estimate)
- Our comprehensive count found 45,936 objects (exact count from all 72 files)
- Difference likely due to sampling methodology vs. complete enumeration

---

## 📝 Key Takeaways

1. **2,053 documents** but **45,936 pages** - most documents are multi-page (avg 22.4 pages)
2. **95.5% are JPG scans** - individual page images, not combined PDFs
3. **95.4% lack OCR** - massive opportunity for improvement
4. **Manageable scale** - 46K pages is substantial but achievable in 1-2 weeks with proper tools
5. **Well-structured** - Clear organization makes systematic processing feasible

---

## 🚀 Recommended Phased Approach

### Phase 1: Proof of Concept
- **Target:** Bosnia-related documents from Blinken series
- **Scale:** ~50-100 records, ~3,000-5,000 pages
- **Timeline:** 2-4 weeks

### Phase 2: Blinken Series
- **Target:** All Antony Blinken files (1994-1998)
- **Scale:** ~1,500 records, ~25,000-30,000 pages
- **Timeline:** 2-3 months

### Phase 3: Full Collection
- **Target:** All four series (1993-2001)
- **Scale:** 2,053 records, 45,936 pages
- **Timeline:** 4-6 months

---

## 📧 Contact Information

**Collection Holder:**
- William J. Clinton Presidential Library
- 1200 President Clinton Avenue
- Little Rock, AR 72201
- Phone: 501-244-2877
- Email: clinton.library@nara.gov

**NARA Catalog:**
- Collection naId: 7388842
- https://catalog.archives.gov/id/7388842
