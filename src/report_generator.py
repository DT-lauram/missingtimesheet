"""Generate missing timesheet reports."""

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd

from src.date_utils import get_last_two_weeks


@dataclass
class WeekRanges:
    """Container for week date ranges."""

    week1_start: datetime
    week1_end: datetime
    week2_start: datetime
    week2_end: datetime


def _build_submitted_weeks_dict(
    submitted_employees: pd.DataFrame,
    weeks: WeekRanges,
) -> dict[int, set[str]]:
    """Build dictionary of submitted weeks by employee.

    Args:
        submitted_employees: DataFrame with EmployeeID and DatePeriod.
        weeks: Week date ranges.

    Returns:
        Dictionary mapping employee ID to set of week ending dates.
    """
    # Convert week ranges to naive datetime for comparison
    week1_start_naive = weeks.week1_start.replace(tzinfo=None)
    week1_end_naive = weeks.week1_end.replace(tzinfo=None)
    week2_start_naive = weeks.week2_start.replace(tzinfo=None)
    week2_end_naive = weeks.week2_end.replace(tzinfo=None)

    submitted_by_employee: dict[int, set[str]] = {}
    for _, row in submitted_employees.iterrows():
        emp_id = int(row["EmployeeID"])

        # Get date period as Python datetime, removing timezone if present
        date_val = row["DatePeriod"]
        date_period = date_val.to_pydatetime() if hasattr(date_val, "to_pydatetime") else date_val

        if hasattr(date_period, "replace"):
            date_period = date_period.replace(tzinfo=None)

        if emp_id not in submitted_by_employee:
            submitted_by_employee[emp_id] = set()

        # Determine which week this timesheet belongs to and store week ending date
        if week1_start_naive <= date_period <= week1_end_naive:
            submitted_by_employee[emp_id].add(weeks.week1_end.strftime("%d/%m/%y"))
        elif week2_start_naive <= date_period <= week2_end_naive:
            submitted_by_employee[emp_id].add(weeks.week2_end.strftime("%d/%m/%y"))

    return submitted_by_employee


def _get_missing_weeks_for_employee(
    submitted_weeks: set[str],
    weeks: WeekRanges,
) -> list[str]:
    """Determine which weeks are missing for an employee.

    Args:
        submitted_weeks: Set of week ending dates with submitted timesheets.
        weeks: Week date ranges.

    Returns:
        List of missing week ending dates formatted as DD/MM/YY.
    """
    # Check which weeks are missing
    missing_weeks = []
    week1_end_str = weeks.week1_end.strftime("%d/%m/%y")
    week2_end_str = weeks.week2_end.strftime("%d/%m/%y")

    if week1_end_str not in submitted_weeks:
        missing_weeks.append(week1_end_str)
    if week2_end_str not in submitted_weeks:
        missing_weeks.append(week2_end_str)

    return missing_weeks


def identify_missing_timesheets(
    all_employees: pd.DataFrame,
    submitted_employees: pd.DataFrame,
    _leave_df: pd.DataFrame,
    exclusion_list: frozenset[int],
    report_date: datetime,
) -> pd.DataFrame:
    """Identify employees with missing timesheets.

    Args:
        all_employees: DataFrame of all employees.
        submitted_employees: DataFrame of employees who submitted timesheets.
        _leave_df: DataFrame of leave history (reserved for future use).
        exclusion_list: Set of employee IDs to exclude from report.
        report_date: Date to calculate reporting period from.

    Returns:
        DataFrame with employees missing timesheets and which weeks are missing.
    """
    # Get date range for reporting period (last two complete weeks)
    _start_date, end_date = get_last_two_weeks(report_date)

    # Calculate individual week ranges
    # Week 2 (most recent): Friday to Thursday
    week2_end = end_date
    week2_start = week2_end - timedelta(days=6)

    # Week 1 (previous week): Friday to Thursday
    week1_end = week2_start - timedelta(days=1)
    week1_start = week1_end - timedelta(days=6)

    weeks = WeekRanges(
        week1_start=week1_start,
        week1_end=week1_end,
        week2_start=week2_start,
        week2_end=week2_end,
    )

    # Build dictionary of submitted timesheets by employee
    submitted_by_employee = _build_submitted_weeks_dict(submitted_employees, weeks)

    missing_list: list[dict[str, int | str]] = []

    for _, employee in all_employees.iterrows():
        emp_id = int(employee["EmployeeID"])

        # Skip if on exclusion list
        if emp_id in exclusion_list:
            continue

        # Skip if employee start date is after the week start
        start_date_val = employee["StartDate"]
        if pd.notna(start_date_val):
            emp_start = pd.to_datetime(start_date_val)
            if hasattr(emp_start, "replace"):
                emp_start = emp_start.replace(tzinfo=None)
            if emp_start > weeks.week1_start.replace(tzinfo=None):
                continue

        # Check which weeks have timesheets
        submitted_weeks = submitted_by_employee.get(emp_id, set())

        # Get missing weeks for this employee
        missing_weeks = _get_missing_weeks_for_employee(submitted_weeks, weeks)

        # Add a separate row for each missing week
        # Store both the formatted string and a date object for sorting
        for i, week_ending in enumerate(missing_weeks):
            # Determine which week this is for sorting
            week_date = weeks.week1_end if i == 0 and week_ending == weeks.week1_end.strftime("%d/%m/%y") else weeks.week2_end
            if week_ending == weeks.week2_end.strftime("%d/%m/%y"):
                week_date = weeks.week2_end
            else:
                week_date = weeks.week1_end

            missing_list.append(
                {
                    "Employee ID": emp_id,
                    "First Name": str(employee["FirstName"]),
                    "Last Name": str(employee["LastName"]),
                    "Week Ending": week_ending,
                    "_sort_date": week_date,
                }
            )

    # Create and sort DataFrame
    missing_df = pd.DataFrame(missing_list)

    if not missing_df.empty:
        # Sort by week ending date (least recent to most recent), then by Employee ID
        missing_df = missing_df.sort_values(["_sort_date", "Employee ID"]).reset_index(drop=True)
        # Remove the temporary sort column
        missing_df = missing_df.drop(columns=["_sort_date"])

    return missing_df


def save_report_to_excel(df: pd.DataFrame, output_path: str) -> None:
    """Save missing timesheet report to Excel file.

    Args:
        df: DataFrame containing missing timesheet data.
        output_path: Path where Excel file should be saved.
    """
    df.to_excel(output_path, index=False, sheet_name="Missing Timesheets")
