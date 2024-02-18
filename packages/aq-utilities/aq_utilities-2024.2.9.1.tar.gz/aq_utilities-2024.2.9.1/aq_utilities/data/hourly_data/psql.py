from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2

from aq_utilities.config.data import CHUNCKSIZE
from aq_utilities.data.remote import download_file


def hourly_predictions_to_postgres(predictions: pd.DataFrame,
                                   engine: "sqlalchemy.engine.Engine",
                                   chunksize: int = CHUNCKSIZE,
                                   verbose: bool = False) -> int:
    """Load hourly data to postgres database."""
    if verbose:
        print(
            f"[{datetime.now()}] writing {len(predictions)} records to postgres"
        )
    try:
        predictions.to_sql(
            "hourly_predictions",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose:
            print(
                f"[{datetime.now()}] wrote {len(predictions)} records to postgres"
            )
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose:
                print(
                    f"[{datetime.now()}] failed to write {len(predictions)} records to postgres with error {e}"
                )
            return 1
    return 0


def hourly_data_to_postgres(hourly_data_fp: str,
                            engine: "sqlalchemy.engine.Engine",
                            chunksize: int = CHUNCKSIZE,
                            verbose: bool = False) -> int:
    """Load hourly data to postgres database."""
    # get timestamp from file name
    timestamp = datetime.strptime(
        Path(hourly_data_fp).stem.split("_")[1].split(".")[0], "%Y%m%d%H")
    if verbose:
        print(f"[{datetime.now()}] loading {hourly_data_fp} to postgres")
    if verbose: print(f"[{datetime.now()}] file timestamp is {timestamp}")
    try:
        names = download_file(fp=hourly_data_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {hourly_data_fp}")
        local_fp, blob_name = names
        df = pd.read_csv(local_fp, sep="|", encoding="latin-1", header=None)
        if verbose: print(f"[{datetime.now()}] read {local_fp}")
    except ValueError as e:
        write_failure_to_postgres((timestamp, hourly_data_fp),
                                  "hourly_data_failures", engine=engine)
        print(e)
        return 1
    df.rename(
        columns={
            0: "date",
            1: "time",
            2: "aqsid",
            3: "name",
            4: "unk",
            5: "measurement",
            6: "units",
            7: "value",
            8: "source"
        }, inplace=True)
    # join date and time columns to make a timestamp column
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"],
                                     format="%m/%d/%y %H:%M")
    df.drop(["date", "time"], axis=1, inplace=True)
    try:
        df.to_sql(
            "hourly_data",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose: print(f"wrote {hourly_data_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose: print(e)
            return 1
    return 0
