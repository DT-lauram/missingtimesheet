"""Configuration constants for missing timesheet report."""

from datetime import UTC, datetime

# Database connection settings
DB_SERVER = "TFS2015SQL"
DB_NAME = "TimeTorque"
DB_USE_WINDOWS_AUTH = True

# File paths
LEAVE_HISTORY_FILE = r"C:\Users\lauram\AI - playground\Missing timesheet report\Leave History 1 Nov. - 1 Dec .xlsx"
OUTPUT_FILE = r"C:\Users\lauram\AI - playground\Missing timesheet report\Missing_Timesheet_Report.xlsx"

# Report date - set to today's date to calculate last two weeks
REPORT_DATE = datetime.now(UTC)

# Timesheet exclusion list
EXCLUSION_LIST = frozenset(
    [
        21,
        63,
        87,
        117,
        147,
        153,
        197,
        202,
        249,
        267,
        290,
        306,
        311,
        316,
        347,
        352,
        359,
        360,
        361,
        390,
        397,
        453,
        500,
        509,
        573,
        596,
        630,
        659,
        660,
        661,
        676,
        684,
        691,
        692,
        708,
        722,
        743,
        746,
        747,
        757,
        788,
        791,
        792,
    ]
)
