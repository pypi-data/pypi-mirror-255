import time
from datetime import datetime
from typing import Union

from sqlalchemy import text
import psycopg2


def get_max_timestamp(table_name: str, timestamp_col_name: str = "timestamp",
                      engine: "sqlalchemy.engine.Engine" = None,
                      verbose: bool = False) -> Union[datetime, None]:
    """Get max timestamp from postgres table."""
    start_date = None
    try:
        with engine.connect() as connection:
            if verbose:
                print(
                    f"[{time.ctime()}] getting max timestamp from {table_name}"
                )
            result = connection.execute(
                text(f"SELECT MAX({timestamp_col_name}) FROM {table_name};"))
            for row in result:
                start_date = row[0]
                if verbose:
                    print(
                        f"[{time.ctime()}] got max timestamp of {start_date} from {table_name}"
                    )
                break
    except Exception as e:
        print(f"failed to get max timestamp from {table_name} with error {e}")
        return None

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    return start_date


def get_min_timestamp(table_name: str, timestamp_col_name: str = "timestamp",
                      engine: "sqlalchemy.engine.Engine" = None,
                      verbose: bool = False) -> Union[datetime, None]:
    """Get min timestamp from postgres table."""
    start_date = None
    try:
        with engine.connect() as connection:
            if verbose:
                print(
                    f"[{time.ctime()}] getting min timestamp from {table_name}"
                )
            result = connection.execute(
                text(f"SELECT MIN({timestamp_col_name}) FROM {table_name};"))
            for row in result:
                start_date = row[0]
                if verbose:
                    print(
                        f"[{time.ctime()}] got min timestamp of {start_date} from {table_name}"
                    )
                break
    except Exception as e:
        print(f"failed to get min timestamp from {table_name} with error {e}")
        return None

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    return start_date
