import json
import os
import numpy as np
from shapely import Point
from ..utils import global_logger

def detect_roundabouts(df):
    """Function to detect roundabouts based on the lat-lon data.

    Args:
        df(pandas.DataFrame): The processed GPS data.

    Returns:
        pandas.DataFrame: Returns the DataFrame with the extension of detection data columns.
    """

    def calculate_bearings(lat1, lon1, lat2, lon2):
        """    Calculates the initial bearing (forward azimuth) from one geographic coordinate to another.

        Args:
            lat1 (float): Latitude of the starting point in decimal degrees.
            lon1 (float): Longitude of the starting point in decimal degrees.
            lat2 (float): Latitude of the destination point in decimal degrees.
            lon2 (float): Longitude of the destination point in decimal degrees.
        Returns:
            float: Bearing in degrees.

        """

        try:
            dLon = np.radians(lon2 - lon1)
            lat1, lat2 = np.radians(lat1), np.radians(lat2)

            x = np.sin(dLon) * np.cos(lat2)
            y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dLon))

            initial_bearing = np.degrees(np.arctan2(x, y))
            compass_bearing = (initial_bearing + 360) % 360

            return compass_bearing
        except Exception as error:
            global_logger.error(f"[ERROR] Error during bearing calculation.")
            global_logger.error(f"[ERROR] {error}")

    def correct_bearing_change(b1, b2):
        """Computes the shortest angular difference between two bearings.

        Args:
            b1 (float): First bearing in degrees.
            b2 (float): Second bearing in degrees.

        Returns:
            float: The smallest angular difference between the two bearings in degrees.

        """

        diff = abs(b2 - b1)
        return min(diff, 360 - diff)

    try:
        global_logger.info("Detecting roundabouts.")
        df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

        bearings = [calculate_bearings(df.iloc[i]['latitude'], df.iloc[i]['longitude'],
                                       df.iloc[i + 1]['latitude'], df.iloc[i + 1]['longitude']) for i in range(len(df) - 1)]
        bearing_changes = [correct_bearing_change(bearings[i], bearings[i + 1]) for i in range(len(bearings) - 1)]

        df = df[:-2].copy()
        df["bearing"] = bearings[:-1]
        df["bearing_change"] = bearing_changes

        window_size = 12
        roundabout_threshold = 420
        global_logger.info(f"Calculating roundabouts using a window size of: {window_size} "
                           f"and roundabout threshold of: {roundabout_threshold}.")
        df["cumulative_turn"] = df["bearing_change"].rolling(window=window_size, min_periods=window_size).sum()
        df["roundabout"] = df["cumulative_turn"] > roundabout_threshold
        df["roundabout_confirmed"] = df["roundabout"] & df["roundabout"].rolling(window=3, min_periods=3).sum().ge(3)

        roundabout_data = df[df["roundabout_confirmed"]][["record_id", "device_timestamp", "latitude", "longitude"]]
        roundabout_data["group"] = (roundabout_data["record_id"].diff() != 1).cumsum()

        json_output = roundabout_data.groupby("group").apply(lambda x: x.drop(columns=["group"]).to_dict(orient="records")).to_dict()
        file_path = os.path.abspath("../roundabout_data.json")
        with open(file_path, "w") as json_file:
            json.dump(json_output, json_file, indent=4)

        print(f"Roundabout data saved to: {file_path}")
        global_logger.info(f"Written the roundabout data to {file_path}.")
        global_logger.info(f"Found {max(roundabout_data['group'])} potential roundabouts.")
        global_logger.info("-" * 50)
        return roundabout_data

    except Exception as error:
        global_logger.error(f"[ERROR] Failed detection roundabout.")
        global_logger.error(f"[ERROR] {error}")
