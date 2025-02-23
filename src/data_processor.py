from .utils import global_logger, MissingIDTracker


def check_missing_database_data(packets):
    """Function to check the database whether it has missing packets based on the IDs."""
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
                              f"microseconds at Record ID: {filterable_id}"
                              f"\nValue difference: {time_diff} microseconds")

    gdf = gdf[gdf["time_diff"] <= 15]
    gdf.drop(columns=["time_diff"], inplace=True)

    global_logger.info(f"Filtered GeoDataFrame for Synchronization errors. "
                       f"Found {len(sync_errors)} problematic row(s).")
    global_logger.info("-" * 50)

    return gdf

def filter_gps_errors(gdf):
    """Checks for GPS errors, if the jump between GPS coordinates exceed 1 degree or the values are invalid.

    Args:

    Returns:

    """
    valid_latitude_range = (-90, 90)
    valid_longitude_range = (-180, 180)
    gdf =


    return
