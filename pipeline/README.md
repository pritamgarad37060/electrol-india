# Electrol India — Election Data Pipeline

A reusable, one-command system to import ANY Indian election data
(Excel/PDF/CSV/JSON) into Supabase and auto-refresh your website.

---

## Quick Start

### 1. Install dependencies (once)
```powershell
.\pipeline\upload.ps1 -Install
```

### 2. Import your data
```powershell
# Assembly election from Excel
.\pipeline\upload.ps1 -File "data\ap_2024.xlsx" -Type assembly -State "Andhra Pradesh" -Year 2024

# Lok Sabha from PDF
.\pipeline\upload.ps1 -File "data\ls_2019.pdf" -Type loksabha -Year 2019

# With separate candidates file (EVM + postal breakdown)
.\pipeline\upload.ps1 -File "data\mh_summary.xlsx" -Cands "data\mh_candidates.xlsx" -Type assembly -State Maharashtra -Year 2024

# Auto-scan entire folder
.\pipeline\upload.ps1 -Scan "data\new_elections\" -Type assembly -Year 2023

# Preview without uploading (dry run)
.\pipeline\upload.ps1 -File "data\test.xlsx" -DryRun -Type assembly -State Bihar -Year 2020

# Replace existing data for an election
.\pipeline\upload.ps1 -File "data\up_2022.xlsx" -Type assembly -State "Uttar Pradesh" -Year 2022 -Replace
```

### 3. Start local server
```powershell
.\pipeline\upload.ps1 -StartServer
# then open http://localhost:8000
```

---

## What It Does

```
Your Excel/PDF/CSV file
        |
        v
[1] Read file (auto-detect format)
        |
        v
[2] Clean & normalize
    - Strip junk rows
    - Parse vote counts, percentages
    - Normalize party codes (BJP, INC, YSRCP, etc.)
    - Calculate missing margins / turnout
        |
        v
[3] Upload to Supabase IN ORDER:
    elections --> states --> parties --> constituencies --> candidates
    (safe to run twice — deduplicates automatically)
        |
        v
[4] Bump website version in index.html
    (forces browser cache refresh)
        |
        v
[5] Log to upload_log.json
```

---

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Excel  | .xlsx     | Any sheet, any column order |
| CSV    | .csv      | UTF-8 or ASCII |
| PDF    | .pdf      | ECI-style tables + text fallback |
| JSON   | .json     | Nested or flat arrays |

---

## Supported Election Types

| Type       | -Type flag   | Example |
|------------|-------------|---------|
| Lok Sabha  | loksabha    | 2024, 2019, 2014... |
| Assembly   | assembly    | Any state, any year |
| By-poll    | bypoll      | AC or PC by-elections |
| Municipal  | municipal   | BMC, MCD, GHMC, BBMP |
| Panchayat  | panchayat   | Gram Panchayat |
| Council    | council     | Legislative Council (MLC) |
| Rajya Sabha| rajyasabha  | Biennial elections |

---

## Excel File Format

Your Excel file can have columns in ANY order with ANY of these names:

| Data | Accepted column names |
|------|-----------------------|
| Constituency No | AC No, AC No., No., Serial, Constituency No |
| Constituency Name | Constituency, AC Name, Name, Seat |
| District | District, Dist, Zila |
| Category | Category, Reservation, Seat Type |
| Electors | Electors, Total Electors, Voters |
| Votes Polled | Votes Polled, Total Votes, Votes Cast |
| Turnout | Turnout, Turnout %, Poll % |
| Winner Name | Winner, Winning Candidate, Elected |
| Winner Party | Winner Party, Winning Party |
| Winner Votes | Winner Votes, Winning Votes |
| Runner-up Name | Runner-up, Runner Up Name |
| Runner-up Party | Runner-up Party |
| Runner-up Votes | Runner-up Votes |
| Margin | Margin, Victory Margin |
| NOTA | NOTA, NOTA Votes |
| Candidates | Candidates, Total Candidates |

---

## Candidates File Format (optional -Cands)

For full candidate breakdown, provide a second file with:

| Column | Accepted names |
|--------|----------------|
| AC No | AC No, No. |
| Candidate Name | Candidate, Candidate Name |
| Party | Party, Party Code |
| Gender | Gender, Sex |
| Age | Age |
| EVM Votes | EVM Votes, General Votes |
| Postal Votes | Postal Votes, Postal |
| Total Votes | Total Votes, Votes |
| Vote % | % of Votes, Vote %, Vote Share |

---

## Configuration (.env)

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

---

## Upload History

Every successful upload is logged in `upload_log.json`:
```json
[
  {
    "timestamp": "2024-10-04T12:00:00",
    "election": "Andhra Pradesh assembly 2024",
    "stats": { "constituencies": 175, "candidates": 2142, "election_id": 5 }
  }
]
```

---

## Adding New State Data

To add a new state or election year:

1. Get the data file (Excel/PDF from ECI or other source)
2. Put it in the `data/` folder
3. Run:
   ```powershell
   .\pipeline\upload.ps1 -File "data\your_file.xlsx" -Type assembly -State "Your State" -Year 2023
   ```
4. Website auto-updates — no code changes needed!
