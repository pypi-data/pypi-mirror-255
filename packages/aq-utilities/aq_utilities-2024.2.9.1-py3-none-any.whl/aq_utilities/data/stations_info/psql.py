from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2

from aq_utilities.config.data import CHUNCKSIZE
from aq_utilities.data.remote import download_file


def stations_info_to_postgres(stations_info_fp: str,
                              engine: "sqlalchemy.engine.Engine",
                              chunksize: int = CHUNCKSIZE,
                              verbose: bool = False) -> int:
    """Load station info data to postgres database."""
    # get timestamp from the directory name
    timestamp_component = Path(stations_info_fp).parent.stem
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

    if verbose:
        print(f"[{datetime.now()}] loading {stations_info_fp} to postgres")

    try:
        names = download_file(fp=stations_info_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {stations_info_fp}")
        local_fp, blob_name = names
        if verbose: print(f"[{datetime.now()}] reading {local_fp}")
        df = pd.read_csv(local_fp, sep="|", encoding="latin-1")
    except Exception as e:
        write_failure_to_postgres((timestamp, stations_info_fp),
                                  "stations_info_failures", engine=engine)
        print(e)
        return 1

    if verbose: print(f"[{datetime.now()}] read {local_fp}")

    df.rename(
        columns={
            "AQSID": "aqsid",
            "FullAQSID": "full_aqsid",
            "StationID": "station_id",
            "Parameter": "parameter",
            "MonitorType": "monitor_type",
            "SiteCode": "site_code",
            "SiteName": "site_name",
            "Status": "status",
            "AgencyID": "agency_id",
            "AgencyName": "agency_name",
            "EPARegion": "epa_region",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Elevation": "elevation",
            "GMTOffset": "gmt_offset",
            "CountryFIPS": "country_fips",
            "CBSA_ID": "cbsa_id",
            "CBSA_Name": "cbsa_name",
            "StateAQSCode": "state_aqs_code",
            "StateAbbreviation": "state_abbreviation",
            "CountyAQSCode": "county_aqs_code",
            "CountyName": "county_name"
        }, inplace=True)
    df.status = df.status.str.upper()
    # add a column with todays date or date of the file
    df["timestamp"] = timestamp

    try:
        df.to_sql(
            "stations_info",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose:
            print(f"[{datetime.now()}] wrote {stations_info_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose: print(e)
            return 1
    return 0
