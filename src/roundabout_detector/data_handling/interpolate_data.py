import numpy as np
import pandas as pd
from itertools import groupby
from scipy.interpolate import interp1d
from ..utils import global_logger
from ..models import MissingIDTracker


def interpolate_missing_records(df):
    """Finds the required ranges and interpolates points where there are at least 5 consecutive missing records.

    Args:
        df(pd.DataFrame): The filtered GPS data.

    Returns:
        pd.DataFrame: The GPS data with the interpolated records.
    """

    def find_consecutive_ranges(nums, min_length=5):
        """Finds the ranges where there are at least 5 consecutive missing records.

        Args:
            nums(list): The list of missing records_ids.
            min_length(int, optional): The min length of consecutive records to be considered. Defaults to 5.

        Returns:
            list: List of tuples which represent the start and end of valid ranges.

        """
        try:
            ranges = []
            for _, group in groupby(enumerate(nums), lambda x: x[0] - x[1]):
                group = list(group)
                seq = [x[1] for x in group]
                if len(seq) >= min_length:
                    ranges.append((seq[0], seq[-1]))
            return ranges
        except Exception as error:
            global_logger(f"[ERROR] Failed finding consecutive ranges. Error: {error}")

    global_logger.info("Interpolating consecutive ranges.")
    missing_id_tracker = MissingIDTracker()
    missing_id_tracker.sort_missing_ids()
    missing_ids = missing_id_tracker.get_missing_ids()

    consecutive_ranges = find_consecutive_ranges(missing_ids, min_length=5)
    columns_to_interpolate = df.columns

    interpolated_record_ids = []
    for from_record_id, to_record_id in consecutive_ranges:
        try:
            df_subset = df[df["record_id"].isin([from_record_id - 1, to_record_id + 1])].set_index("record_id")
            record_ids = np.arange(from_record_id, to_record_id + 1)  # Exclude from_record_id and to_record_id

            interpolated_values = {"record_id": record_ids}
            for col in columns_to_interpolate:
                if col=="record_id":
                    continue

                interpolator = interp1d([from_record_id - 1, to_record_id + 1], df_subset[col].values, kind="linear")
                interpolated_values[col] = interpolator(record_ids)

            df = pd.concat([df, pd.DataFrame(interpolated_values)], ignore_index=True)
            df = df.sort_values(by="record_id").reset_index(drop=True)
            interpolated_record_ids.extend(map(int, interpolated_values["record_id"]))
        except Exception as error:
            global_logger.error(f"[ERROR] Interpolation error, "
                                f"failed interpolating record_id range: {from_record_id}, {to_record_id}")
            global_logger.error(f"[ERROR] {error}")

        global_logger.info(f"Interpolated {len(interpolated_record_ids)} records.")
        global_logger.info(f"Interpolated records with IDs: {interpolated_record_ids}")
        global_logger.info("Done interpolating consecutive ranges.")
        global_logger.info("-" * 50)

    return df

