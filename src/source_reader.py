import struct
import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from .utils import global_logger
from .exceptions import TableUnavailableException


def read_database(db_path):
    """Reads sensor index databases. Reads the following tables: Sensor, Packet
    Identifies missing rows from the database based on the packet_id column. Logs them if there are any missing ones.

    Args:
        db_path(str): The path to the database to process.

    Returns:
        pd.DataFrame: A pandas dataframe which contains the "Packet" column from the input data.
    """

    global_logger.info("Reading Database!")
    conn = sqlite3.connect(db_path)

    table_names_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql(table_names_query, conn).name.tolist()

    if "Sensor" in tables_df:
        sensor_query = "SELECT name FROM Sensor"
        sensors = pd.read_sql_query(sensor_query, conn)
        global_logger.info(f"Sensors used: {', '.join(sensors['name'].tolist())}")
    else:
        global_logger.warning("[WARNING] Missing Sensor table in database.")

    if "Packet" in tables_df:
        packet_query = "SELECT packet_id, sensor_id, synced_timestamp, offset, size FROM Packet"
        packets = pd.read_sql_query(packet_query, conn)
    else:
        raise TableUnavailableException("Packet")


    global_logger.info(f"Successfully read {len(packets)} rows from the database!")
    global_logger.info("-" * 50)
    return packets


def read_binary_file(path, packets):
    """Function which reads the given GPS Data Binary File, reads the header and the records from the binary file.

    The Header contains:
        - version (4 bytes)
        - count (4 bytes) (The number of records found inside the file)
        - crc (8 bytes) (SHA-256 calculated hash, a 64-bit CRC)

    Assumes, that the records in the binary file are defined this way:
        - record_id (4 bytes, 32-bit integer)
        - synced_timestamp (8 bytes) (microseconds epoch)
        - device_timestamp (8 bytes) (nanoseconds epoch)
        - latitude (8 bytes)
        - longitude (8 bytes)
        - altitude (4 bytes)

    Args:
        path(str): The path to the binary file.
        packets(pandas.DataFrame): The data from the Packet table, read from the database stored in a Pandas DataFrame.

    Returns:
        geopandas.GeoDataFrame: A GeoDataFrame, which stores the processed data from the binary file.
    """

    header_format = 'IIQ'
    header_size = struct.calcsize(header_format)

    record_format = "=IQQddf"
    record_size = struct.calcsize(record_format)

    global_logger.info("Reading binary file!")
    with open(path, "rb") as file:
        raw_data = file.read()

        header_source = raw_data[:header_size]
        try:
            version, record_count, crc = struct.unpack(header_format, header_source)
            global_logger.info(f"Header data found! Version: {version} | Record Count: {record_count} | "
                           f"Crc: {'Available' if crc else 'Unavailable'}")
        except Exception as error:
            global_logger.error("ERROR: Failed reading header of the binary file.")
            global_logger.error(f"ERROR: {error}")

        data = []
        append_data = data.append
        unpack = struct.unpack_from
        for offset, size in zip(packets["offset"], packets["size"]):
            if size != record_size:
                global_logger.warning(f"[WARNING] Record size at offset {offset} is incorrect. Skipping record.")
                continue

            (record_id, synced_timestamp, device_timestamp,
             latitude, longitude, altitude) = unpack(record_format, raw_data, offset)

            device_timestamp = round(device_timestamp / 1000)  # Convert nanoseconds epoch to microseconds epoch

            append_data((record_id, synced_timestamp, device_timestamp, latitude, longitude, altitude))

    global_logger.info(f"Successfully read {len(data)} records from the binary file.")
    global_logger.info("-" * 50)
    return gpd.GeoDataFrame(data, columns=["record_id", "synced_timestamp", "device_timestamp", "latitude",
                                          "longitude", "altitude"])

