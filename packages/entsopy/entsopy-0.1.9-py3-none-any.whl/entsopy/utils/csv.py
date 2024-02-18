import pandas as pd
from datetime import datetime


def concat_and_save_dfs(
    dfs: list,
    file_name: str,
    suffix: str = "",
    timestamp: str = (datetime.now()).strftime("%Y%m%dT%H%M%S"),
    download_dir: str = "",
) -> str:
    """
    Concatenates a list of DataFrames and saves the result as a CSV file.

    Args:
        dfs (list): A list of DataFrames to be concatenated.
        file_name (str): The base name of the output file.
        suffix (str, optional): A suffix to be added to the file name (default: "").
        timestamp (str, optional): A timestamp to be added to the file name (default: current timestamp).

    Returns:
        str: The name of the saved CSV file.

    """

    res = pd.concat(dfs, join="outer").fillna("na")
    timestamp = (datetime.now()).strftime("%Y%m%dT%H%M%S")
    file_saving_name = f"{file_name}-{suffix}-{timestamp}.csv"
    print(f"{download_dir}/{file_saving_name}")
    res.to_csv(f"{download_dir}/{file_saving_name}", index=True, index_label="id")
    return file_saving_name
