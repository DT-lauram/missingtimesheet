# Missing Timesheet Report - Instructions

## Goal
Generate a report of employees with missing timesheets by analyzing submitted timesheets and leave data.

## Reporting Period
- Report covers the **last two complete weeks**
- Dynamically calculated based on current date
- Each missing week appears as a **separate row** in the report
- Week ending dates shown in **DD/MM/YY format** (e.g., 28/11/25)

## Data Sources

### TimeTorque Database
- **Server**: TFS2015SQL
- **Database**: TimeTorque
- **Tables Used**:
  - `Employee` - Active employee list with start dates
  - `TimeSheet_Entry` - Submitted timesheet records
  - `TimesheetExclusions` - Employees excluded from reporting

### Leave History File
- **Format**: Excel file (.xlsx)
- **Columns Used**:
  - Column A: Employee ID
  - Column E: Leave dates/periods
- **Current File**: `Leave History 1 Nov. - 1 Dec .xlsx`

## Data Linking
- **Employee ID** is used to link data between all sources

## Week Definition
- A week is defined as **Friday to Thursday**
- Week ending date is always a **Thursday**
- Example: Week of Nov 22-28 ends on Thursday, Nov 28

## Missing Timesheet Logic

### Employees ARE included in report if:
- No timesheet submitted for the week
- NOT on leave for the entire week
- NOT on the timesheet exclusion list
- Start date is BEFORE the beginning of the timesheet week

### Employees are EXCLUDED from report if:
- ✅ Timesheet has been submitted for the week
- ✅ They have a record of leave covering the whole week (Friday-Thursday)
- ✅ They appear in the `TimesheetExclusions` database table
- ✅ Their start date is after the start of the timesheet week

## Report Output Format

### Columns
1. **Employee ID** - Unique identifier
2. **First Name** - Employee's first name
3. **Last Name** - Employee's last name
4. **Week Ending** - Date in DD/MM/YY format (Thursday)

### Row Format
- Each missing week appears as a **separate row**
- If an employee is missing both weeks, they appear **twice** with different week ending dates

### Sort Order
1. **Primary**: Week Ending date (oldest to newest)
2. **Secondary**: Employee ID (ascending)

## Example Output

| Employee ID | First Name | Last Name | Week Ending |
|-------------|------------|-----------|-------------|
| 506         | Nick       | Bell      | 28/11/25    |
| 715         | Robert     | Higgins   | 28/11/25    |
| 138         | Blaire     | Alder     | 05/12/25    |
| 506         | Nick       | Bell      | 05/12/25    |
| 715         | Robert     | Higgins   | 05/12/25    |

In this example:
- Nick Bell (506) and Robert Higgins (715) are missing both weeks
- Blaire Alder (138) is only missing week ending 05/12/25

## Ad-Hoc Query: People on Leave with Timesheet Requirements

### Purpose
Identify employees who are on leave for a specific period AND are required to submit timesheets (partial timesheets).

### Data Sources Required
1. **Leave History File**: `leave-history-46243-2026-jan-07.xlsx`
   - Contains leave records with dates, names, and leave types
2. **Regional People Allocations File**: `Regional people allocations LIVE.xlsx`
   - Sheet: "Regional allocations LIVE"
   - Header row: Row 3 (index 2)

### Key Filters
1. **Timesheet? = Y**: Employee submits timesheets
2. **Partial? = Y**: Employee submits partial timesheets (e.g., contractors, part-time)
3. **Leave dates**: Must be on leave for ALL days in the specified period

### Example Query Process

To find people on leave Jan 5-8 who need to submit partial timesheets:

```python
import pandas as pd
from datetime import datetime

# 1. Read leave history
leave_df = pd.read_excel('leave-history-46243-2026-jan-07.xlsx')
start_date = datetime(2026, 1, 5)
end_date = datetime(2026, 1, 8)
leave_in_range = leave_df[(leave_df['Date'] >= start_date) & (leave_df['Date'] <= end_date)]

# 2. Read regional allocations (header on row 3)
regional_df = pd.read_excel('Regional people allocations LIVE.xlsx',
                            sheet_name='Regional allocations LIVE',
                            header=2)

# 3. Filter for Timesheet? = Y AND Partial? = Y
filtered = regional_df[(regional_df['Timesheet?'] == 'Y') &
                       (regional_df['Partial? '] == 'Y')]

# 4. Match names and verify all 4 days covered
# (Implementation handles name variations like "Catherine (Cat)" vs "Catherine")
```

### Name Matching Considerations
- Regional data may use abbreviated names: "Mark" vs "Mark Phillip"
- Regional data may include nicknames: "Catherine (Cat)" vs "Catherine"
- Leave data format: "SURNAME, First Names (Preferred Name)"
- Matching strategy: Compare surnames exactly, then check if first names match or start with each other

### Example Results (Jan 5-8, 2026)
11 people matched criteria:
- ARZOLA, Mark - Senior Developer, Asia Pacific
- DELLOW, Phillip (Phil) - Senior DevOps Engineer, Technology
- EAGLE, Jonathan - Engineering Lead, Asia Pacific
- FLANNERY, Siobhan - Senior Project Coordinator, Engineering (0.8 FTE)
- HARVISON, James - Practice Lead, Solutions Design, Engineering
- KEANE, Hayley - Data Engineer, Advisory Data & AI
- MCCARTHY, Daniel - Senior Developer, Engineering
- MCINDOE, Jamie - Delivery Lead, Technology
- NICOL, Craig - Senior Test Analyst, Engineering
- RUVANDO, Maureen - Senior Project Coordinator, Asia Pacific
- SPIERS, Catherine (Cat) - Senior Test Analyst, Asia Pacific (0.65 FTE)

### Notes
- Part-time employees (FTE < 1.0) typically require partial timesheets
- All matched employees must be on leave for the ENTIRE period (all specified days)
- This is separate from the main missing timesheet report

## Technical Implementation

### Configuration
Settings are in `src/config.py`:
- Database connection details
- File paths
- Report date (defaults to current date)

### Running the Report
```bash
# 1. Connect to VPN
# 2. Run the report
uv run python -m src.main

# 3. Open the generated report
start "Missing_Timesheet_Report.xlsx"
```

### Database Tables Reference

**TimesheetExclusions Table**
- Contains Employee IDs to exclude from all timesheet reports
- Checked via: `SELECT DISTINCT EmployeeID FROM TimesheetExclusions` 




