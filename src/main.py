"""Main script to generate missing timesheet report."""

import logging

from src.config import (
    DB_NAME,
    DB_SERVER,
    DB_USE_WINDOWS_AUTH,
    LEAVE_HISTORY_FILE,
    OUTPUT_FILE,
    REPORT_DATE,
)
from src.database import (
    create_connection,
    get_all_employees,
    get_submitted_timesheets,
    get_timesheet_exclusions,
)
from src.date_utils import get_last_two_weeks
from src.leave_parser import load_leave_history
from src.report_generator import identify_missing_timesheets, save_report_to_excel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Execute the missing timesheet report generation."""
    try:
        logger.info("Starting missing timesheet report generation")
        logger.info("Report date: %s", REPORT_DATE.strftime("%Y-%m-%d"))

        # Calculate date range
        start_date, end_date = get_last_two_weeks(REPORT_DATE)
        logger.info("Reporting period: %s to %s", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        # Connect to database
        logger.info("Connecting to database: %s on %s", DB_NAME, DB_SERVER)
        conn = create_connection(DB_SERVER, DB_NAME, DB_USE_WINDOWS_AUTH)
        logger.info("Database connection established")

        # Get employee data
        logger.info("Retrieving employee list")
        all_employees = get_all_employees(conn)
        logger.info("Found %d employees", len(all_employees))

        # Get exclusion list from database
        logger.info("Retrieving timesheet exclusions")
        exclusion_list = get_timesheet_exclusions(conn)
        logger.info("Found %d employees on exclusion list", len(exclusion_list))

        # Get submitted timesheets
        logger.info("Retrieving submitted timesheets")
        submitted = get_submitted_timesheets(conn, start_date, end_date)
        logger.info("Found %d employees with submitted timesheets", len(submitted))

        # Close database connection
        conn.close()
        logger.info("Database connection closed")

        # Load leave history
        logger.info("Loading leave history from: %s", LEAVE_HISTORY_FILE)
        leave_data = load_leave_history(LEAVE_HISTORY_FILE)
        logger.info("Leave history loaded: %d records", len(leave_data))

        # Generate missing timesheet report
        logger.info("Identifying employees with missing timesheets")
        missing_df = identify_missing_timesheets(
            all_employees,
            submitted,
            leave_data,
            exclusion_list,
            REPORT_DATE,
        )
        logger.info("Found %d employees with missing timesheets", len(missing_df))

        # Save report
        logger.info("Saving report to: %s", OUTPUT_FILE)
        save_report_to_excel(missing_df, OUTPUT_FILE)
        logger.info("Report saved successfully")

        # Display summary
        logger.info("=" * 60)
        logger.info("MISSING TIMESHEET REPORT SUMMARY")
        logger.info("=" * 60)
        logger.info("Total employees: %d", len(all_employees))
        logger.info("Employees with timesheets: %d", len(submitted))
        logger.info("Excluded employees: %d", len(exclusion_list))
        logger.info("Missing timesheets: %d", len(missing_df))
        logger.info("=" * 60)

        if not missing_df.empty:
            logger.info("\nEmployees with missing timesheets:")
            for _, row in missing_df.iterrows():
                logger.info("  %d - %s %s", row["Employee ID"], row["First Name"], row["Last Name"])

    except Exception:
        logger.exception("Error generating report")
        raise


if __name__ == "__main__":
    main()
