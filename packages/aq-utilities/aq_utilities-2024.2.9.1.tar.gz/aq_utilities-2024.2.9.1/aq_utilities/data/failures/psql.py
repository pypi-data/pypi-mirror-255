from datetime import datetime
from typing import Tuple, Union

import pandas as pd
import psycopg2

from aq_utilities.config.data import CHUNCKSIZE


def write_failure_to_postgres(failed_request: Tuple["datetime", str],
                              target_table_name: str,
                              chunksize: int = CHUNCKSIZE,
                              engine: "sqlalchemy.engine.Engine" = None,
                              verbose: bool = False) -> None:
    """Write failure to postgres database."""
    # the schema for failures is constant (cols timestamp and request)
    df = pd.DataFrame([failed_request], columns=["timestamp", "request"])
    df.timestamp = pd.to_datetime(df.timestamp)
    try:
        if verbose:
            print(
                f"[{datetime.now()}] writing failure {failed_request} to postgres table {table_name}"
            )
        df.to_sql(
            target_table_name,
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose: print(f"[{datetime.now()}] wrote failure")
    except Exception as e:
        print(f"failed to write failure to postgres: {e}")
