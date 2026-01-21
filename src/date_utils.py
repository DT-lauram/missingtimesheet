"""Date utility functions for timesheet reporting."""

from datetime import datetime, timedelta


def get_last_two_weeks(report_date: datetime) -> tuple[datetime, datetime]:
    """Calculate the date range for reporting period.

    A week is defined as Friday to Thursday.
    Returns the last two complete weeks.

    Args:
        report_date: The date from which to calculate backwards.

    Returns:
        A tuple of (start_date, end_date) representing the reporting period.
    """
    # Find the most recent Thursday (end of current/last week)
    # Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
    days_since_thursday = (report_date.weekday() - 3) % 7
    if days_since_thursday == 0 and report_date.weekday() != 3:
        days_since_thursday = 7

    last_thursday = report_date - timedelta(days=days_since_thursday)

    # Calculate two weeks back from that Thursday
    # Week 1: Friday to Thursday (most recent complete week)
    week1_end = last_thursday
    week1_start = week1_end - timedelta(days=6)

    # Week 2: Friday to Thursday (second most recent complete week)
    week2_end = week1_start - timedelta(days=1)
    week2_start = week2_end - timedelta(days=6)

    return week2_start, week1_end


def is_full_week_covered(
    leave_start: datetime | None,
    leave_end: datetime | None,
    week_start: datetime,
    week_end: datetime,
) -> bool:
    """Check if leave period covers the entire week.

    Args:
        leave_start: Start date of leave period (None if no leave).
        leave_end: End date of leave period (None if no leave).
        week_start: Start date of the week (Friday).
        week_end: End date of the week (Thursday).

    Returns:
        True if the leave covers the entire week, False otherwise.
    """
    if leave_start is None or leave_end is None:
        return False

    return leave_start <= week_start and leave_end >= week_end
