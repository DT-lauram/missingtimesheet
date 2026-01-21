"""Database connection and query functions for TimeTorque."""

from datetime import datetime

import pandas as pd
import pyodbc


def get_connection_string(server: str, database: str, use_windows_auth: bool) -> str:
    """Build SQL Server connection string.

    Args:
        server: SQL Server instance name.
        database: Database name.
        use_windows_auth: Whether to use Windows authentication.

    Returns:
        A pyodbc connection string.
    """
    if use_windows_auth:
        return f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    msg = "SQL Server authentication not implemented"
    raise NotImplementedError(msg)


def create_connection(server: str, database: str, use_windows_auth: bool) -> pyodbc.Connection:
    """Create a connection to the SQL Server database.

    Args:
        server: SQL Server instance name.
        database: Database name.
        use_windows_auth: Whether to use Windows authentication.

    Returns:
        A pyodbc Connection object.

    Raises:
        pyodbc.Error: If connection fails.
    """
    conn_str = get_connection_string(server, database, use_windows_auth)
    return pyodbc.connect(conn_str)


def get_all_employees(conn: pyodbc.Connection) -> pd.DataFrame:
    """Retrieve all active employees from the database.

    Args:
        conn: Active database connection.

    Returns:
        DataFrame with columns: EmployeeID, FirstName, LastName, StartDate.

    Raises:
        pyodbc.Error: If query fails.
    """
    query = """
    SELECT
        EmployeeID,
        FirstName,
        LastName,
        StartDate
    FROM Employee
    WHERE Active = -1
    """
    return pd.read_sql(query, conn)


def get_timesheet_exclusions(conn: pyodbc.Connection) -> frozenset[int]:
    """Retrieve employee IDs from the timesheet exclusion list.

    Args:
        conn: Active database connection.

    Returns:
        Frozenset of employee IDs to exclude from timesheet reports.

    Raises:
        pyodbc.Error: If query fails.
    """
    query = """
    SELECT DISTINCT EmployeeID
    FROM TimesheetExclusions
    """
    df = pd.read_sql(query, conn)
    return frozenset(df["EmployeeID"].astype(int).tolist())


def get_submitted_timesheets(
    conn: pyodbc.Connection,
    start_date: datetime,
    end_date: datetime,
) -> pd.DataFrame:
    """Retrieve submitted timesheets for the date range.

    Args:
        conn: Active database connection.
        start_date: Start of reporting period.
        end_date: End of reporting period.

    Returns:
        DataFrame with EmployeeID and DatePeriod for submitted timesheets.

    Raises:
        pyodbc.Error: If query fails.
    """
    query = """
    SELECT DISTINCT
        EmployeeID,
        DatePeriod
    FROM TimeSheet_Entry
    WHERE DatePeriod BETWEEN ? AND ?
    AND Submitted = 1
    """
    return pd.read_sql(query, conn, params=[start_date, end_date])
