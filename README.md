# Missing Timesheet Report Generator

This project generates reports of employees with missing timesheets by querying the TimeTorque database and cross-referencing with leave history data.

## Requirements

- [uv](https://docs.astral.sh/uv/) - Python package and project manager (manages Python automatically)
- [just](https://github.com/casey/just) - Command runner
- VPN access to TimeTorque SQL Server database (TFS2015SQL)
- Leave history Excel file

## Setup

```bash
just dev-setup
```

This will automatically install Python 3.13 and all dependencies via `uv`.

## Usage

1. Connect to VPN (required for database access)
2. Run the report generator:

```bash
uv run python -m src.main
```

3. Open the generated report:

```bash
start "Missing_Timesheet_Report.xlsx"
```

## Configuration

Edit `src/config.py` to customize:
- Database server and connection settings
- File paths for leave history and output report
- Report date (defaults to current date)

## Output

The script generates `Missing_Timesheet_Report.xlsx` with the following columns:
- **Employee ID**: Unique employee identifier
- **First Name**: Employee's first name
- **Last Name**: Employee's last name
- **Week Ending**: Date the timesheet week ends (Thursday) in DD/MM/YY format

### Report Details

- **Reporting Period**: Last two complete weeks (Friday to Thursday)
- **Week Definition**: Friday through Thursday
- **Date Format**: DD/MM/YY (e.g., 28/11/25)
- **Row Format**: Each missing week appears as a separate row
  - Employees missing one week: 1 row
  - Employees missing both weeks: 2 rows
- **Sort Order**: By week ending date (oldest first), then by Employee ID

### Exclusion Logic

Employees are excluded from the report if:
- They have submitted their timesheet for the week
- They are on the timesheet exclusion list (from `TimesheetExclusions` database table)
- Their start date is after the beginning of the reporting period

## Project Structure

```
src/
├── main.py              # Main entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and queries
├── date_utils.py        # Date calculation utilities
├── leave_parser.py      # Leave history Excel file parser
└── report_generator.py  # Report generation logic
```

## Development

### Code Quality

Run quality checks before committing:

```bash
just check          # Run all checks (linting, formatting, type checking)
just format         # Auto-format code
just lint           # Run linting only
just typecheck      # Run type checking only
```

### Testing

```bash
just test           # Run all tests
just test-cov       # Run tests with coverage report
```

## Ad-Hoc Queries

### People on Leave with Timesheet Requirements

You can identify employees on leave for a specific period who need to submit partial timesheets by cross-referencing:
- Leave history data (`leave-history-46243-2026-jan-07.xlsx`)
- Regional people allocations (`Regional people allocations LIVE.xlsx`)

Key filters:
- **Timesheet? = Y**: Employee submits timesheets
- **Partial? = Y**: Employee submits partial timesheets
- Must be on leave for ALL days in the specified period

See `Missing timesheet report instructions.md` for detailed query process and examples.

## Notes

- The report dynamically calculates the last two complete weeks based on the current date
- A week ending on Thursday means the timesheet period is Friday through Thursday
- VPN connection is required to access the TimeTorque database on TFS2015SQL
- Ad-hoc queries for leave analysis can be performed using the Excel files without VPN access
