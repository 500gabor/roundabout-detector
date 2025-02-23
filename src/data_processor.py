from .utils import global_logger, MissingIDTracker


def check_missing_database_data(packets):
    """Function to check the database whether it has missing packets based on the IDs.

    Args:
        packets(pandas.DataFrame): The data read from the SQLite Database.

    """

    global_logger.info("Checking database for missing record_id's.")

    missing_id_tracker = MissingIDTracker()
    packet_ids = packets["packet_id"]
    for current_id, next_id in zip(packet_ids, packet_ids[1:]):
        if current_id + 1 != next_id:
            missing_id_tracker.add_missing_id(current_id + 1)
            global_logger.info(f"[WARNING] Missing Packet ID: {current_id + 1}")
    global_logger.info("Done checking database for missing record_ids.")
    global_logger.info("-" * 50)

    return


def filter_invalid_timestamps(gdf):
    """Processes the data originally coming from the binary file, filters rows where the difference between the
    device_timestamp and the synced_timestamp exceed 15 microseconds. Logs the data according.

    Args:
        gdf(gpd.GeoDataFrame): The GPS data originally coming from the binary file.

    Returns:
        gpd.GeoDataFrame: The filtered GeoDataFrame.

    """

    global_logger.info("Filtering GeoDataFrame for Synchronization errors.")

    missing_id_tracker = MissingIDTracker()
    gdf = gdf.assign(time_diff=abs(gdf["device_timestamp"] - gdf["synced_timestamp"]))

    sync_errors = gdf[gdf["time_diff"] > 15]
    for filterable_id, time_diff in zip(sync_errors["record_id"], sync_errors["time_diff"]):
        missing_id_tracker.add_missing_id(filterable_id)
        global_logger.warning(f"[ERROR] Synchronization Error: device_timestamp and synced_timestamp values exceed 15 "
                              f"\n\tmicroseconds at Record ID: {filterable_id} "
                              f"Value difference: {time_diff} microseconds")

    gdf = gdf[gdf["time_diff"] <= 15]
    gdf.drop(columns=["time_diff"], inplace=True)

    global_logger.info(f"Filtered GeoDataFrame for Synchronization errors. "
                       f"Found {len(sync_errors)} problematic row(s).")
    global_logger.info("-" * 50)

    return gdf

def filter_gps_errors(gdf):
    """Checks for GPS errors, if the jump between GPS coordinates exceed 1 degree or the values are invalid.

    Args:
        gdf(gpd.GeoDataFrame): The GPS data originally coming from the binary file.
    Returns:
        gpd.GeoDataFrame: The filtered GeoDataFrame.

    """

    def log_removed_rows(row):
        global_logger.error(f"[ERROR] GPS Error: Removed row: {row['record_id']} "
                            f"with latitude: {row['latitude']}, longitude: {row['longitude']}")
        missing_id_tracker.add_missing_id(int(row['record_id']))

    global_logger.info("Filtering GPS Errors.")
    missing_id_tracker = MissingIDTracker()

    #  Validating latitude and longitude range between -90 and 90 or -180 and 180 degrees.
    valid_latitude_range = (-90, 90)
    valid_longitude_range = (-180, 180)
    gdf_filtered = gdf[
        (gdf["latitude"].between(*valid_latitude_range)) &
        (gdf["longitude"].between(*valid_longitude_range))
        ].copy()

    removed_rows = gdf.loc[~gdf.index.isin(gdf_filtered.index)]
    global_logger.info(f"Found and dropped {len(removed_rows)} rows based on validity range of latitude and longitude.")
    removed_rows.apply(log_removed_rows, axis=1)

    #  Validating for GPS jumps
    gdf = gdf_filtered.copy()
    del gdf_filtered
    del removed_rows
    gdf["lat_diff_next"] = gdf["latitude"].diff(periods=-1).abs()
    gdf["lon_diff_next"] = gdf["longitude"].diff(periods=-1).abs()

    problematic_rows = gdf[(gdf["lat_diff_next"] > 1) | (gdf["lon_diff_next"] > 1)].index.tolist()
    problematic_rows = [index for index in problematic_rows if index - 1 in problematic_rows]
    dropped_records = gdf.loc[problematic_rows, ["record_id", "latitude", "longitude"]].to_records(index=False).tolist()
    gdf_filtered = gdf[~gdf.index.isin(problematic_rows)].copy()
    gdf_filtered.drop(columns=["lat_diff_next", "lon_diff_next"], inplace=True)

    for record_id, lat, lon in dropped_records:
        missing_id_tracker.add_missing_id(record_id)
        global_logger.error(f"[ERROR] GPS Error: Found jump in the GPS coordinate values for the record with "
                            f"\n\tRecord ID: {record_id}, latitude: {lat}, longitude: {lon}")

    global_logger.info("Filtered GPS Errors.")
    global_logger.info("-" * 50)
    return gdf_filtered
