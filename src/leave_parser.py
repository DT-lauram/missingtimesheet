"""Parse and process leave history data from Excel."""

from datetime import datetime

import pandas as pd


def load_leave_history(file_path: str) -> pd.DataFrame:
    """Load leave history from Excel file.

    Args:
        file_path: Path to the Excel file containing leave history.

    Returns:
        DataFrame with leave history data.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file format is invalid.
    """
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError as e:
        msg = f"Leave history file not found: {file_path}"
        raise FileNotFoundError(msg) from e
    except Exception as e:
        msg = f"Error reading leave history file: {e}"
        raise ValueError(msg) from e

    return df


def get_employee_leave_periods(
    leave_df: pd.DataFrame,
    employee_id: int,
) -> list[tuple[datetime, datetime]]:
    """Extract leave periods for a specific employee.

    Args:
        leave_df: DataFrame containing leave history.
        employee_id: The employee ID to filter for.

    Returns:
        List of tuples containing (start_date, end_date) for each leave period.
    """
    # Column A should contain Employee ID, Column E should contain leave dates
    # This is a simplified implementation - adjust based on actual data structure

    if leave_df.empty:
        return []

    # Try to find employee ID in first column
    first_col = leave_df.columns[0]

    try:
        employee_leaves = leave_df[leave_df[first_col] == employee_id]
    except (KeyError, IndexError):
        return []

    if employee_leaves.empty:
        return []

    # Extract leave periods from column E (index 4)
    leave_periods: list[tuple[datetime, datetime]] = []

    # This needs to be implemented based on actual data structure
    # For now, return empty list
    return leave_periods


def has_full_week_leave(
    leave_df: pd.DataFrame,
    employee_id: int,
    week_start: datetime,
    week_end: datetime,
) -> bool:
    """Check if employee has leave covering entire week.

    Args:
        leave_df: DataFrame containing leave history.
        employee_id: The employee ID to check.
        week_start: Start of the week (Friday).
        week_end: End of the week (Thursday).

    Returns:
        True if employee has leave for the entire week, False otherwise.
    """
    leave_periods = get_employee_leave_periods(leave_df, employee_id)
    return any(start <= week_start and end >= week_end for start, end in leave_periods)
