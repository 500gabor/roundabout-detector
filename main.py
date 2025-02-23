from src import (read_database, read_binary_file, check_missing_database_data,
                 filter_invalid_timestamps, filter_gps_errors)
from src.utils import MissingIDTracker


packets = read_database(r"C:\work\aimotive\sensor_index.db")
check_missing_database_data(packets)
gdf = read_binary_file(r"C:\work\aimotive\gps_data.bin", packets)
filter_invalid_timestamps(gdf)
filter_gps_errors(gdf)

missing_id_tracker = MissingIDTracker()
print(missing_id_tracker.get_missing_ids())
gdf.to_csv("asd.csv")

print("Stop")