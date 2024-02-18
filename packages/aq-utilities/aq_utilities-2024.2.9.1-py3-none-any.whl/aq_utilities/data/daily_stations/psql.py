from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import psycopg2

from aq_utilities.config import CHUNCKSIZE
from aq_utilities.data.remote import download_file


def daily_stations_to_postgres(daily_stations_fp: str,
                               engine: "sqlalchemy.engine.Engine",
                               chunksize: int = CHUNCKSIZE,
                               verbose: bool = False) -> int:
    """Load daily stations data to postgres database."""
    # get timestamp from the directory name
    timestamp_component = Path(daily_stations_fp).parent.stem
    if verbose:
        print(f"[{datetime.now()}] loading {daily_stations_fp} to postgres")
    if verbose: print(f"[{datetime.now()}] file timestamp is {timestamp}")
    if timestamp_component == "today":
        timestamp = datetime.utcnow()
        timestamp = timestamp.replace(hour=0, minute=0, second=0,
                                      microsecond=0)
    elif timestamp_component == "yesterday":
        timestamp = datetime.utcnow() - timedelta(days=1)
        timestamp = timestamp.replace(hour=0, minute=0, second=0,
                                      microsecond=0)
    else:
        timestamp = datetime.strptime(timestamp_component, "%Y%m%d")
    try:
        names = download_file(fp=daily_stations_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {daily_stations_fp}")
        local_fp, blob_name = names
        df = df = pd.read_csv(local_fp, sep="|", encoding="latin-1",
                              header=None)
        if verbose: print(f"[{datetime.now()}] read {local_fp}")
    except ValueError as e:
        write_failure_to_postgres((timestamp, daily_stations_fp),
                                  "daily_stations_failures", engine=engine)
        print(e)
        return 1
    df = df[[0, 1, 4, 8, 9]]
    # obtain list of unique values for each column based on StationID
    df = df.groupby(0).agg(lambda x: list(sorted(np.unique(x)))
                           if x.name == 1 else x.iloc[0])
    df.rename(
        columns={
            0: "aqsid",
            1: "parameters",
            4: "status",
            8: "latitude",
            9: "longitude"
        }, inplace=True)
    # cast status to upper case
    df.status = df.status.str.upper()
    # add a column with todays date or date of the file
    df["timestamp"] = timestamp
    df = df.rename_axis("aqsid").reset_index()

    try:
        df.to_sql(
            "daily_stations",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose: print(f"wrote {daily_stations_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            print(e)
            return 1
    return 0
