from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from typing import Tuple, Union


def download_file(
    fp: str,
    timestamp: datetime,
) -> Union[Tuple[str, str], None]:
    """Download the file at fp and save it to disk.
    
    Args:
        fp: the url of the file to download
        timestamp: the timestamp to use for the blob name

    Returns:
        name, blob_name: the name of the file on disk and the name of the blob
    """
    # download the file to local storage
    with urlopen(fp) as response:
        # read the file
        try:
            data = response.read()
        except Exception as e:
            raise ValueError(f"failed to read file at {fp} with error {e}")
        # determine the file name
        name = Path(fp).name
        # construct the blob name using the timestamp
        blob_name = f"{timestamp.year}/{timestamp.month}/{timestamp.day}/{name}"
        # save the data to disk
        with open(name, "wb") as f:
            f.write(data)
        return name, blob_name
