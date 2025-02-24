import argparse
import sys
import os
from roundabout_detector import (read_database, read_binary_file, check_missing_database_data,filter_invalid_timestamps,
                                 filter_gps_errors, interpolate_missing_records, visualize_map, detect_roundabouts)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    parser = argparse.ArgumentParser(description="Process GPS binary alongside database data and detect roundabouts.")

    parser.add_argument("--db_path", required=True, help="Path to the sensor index database")
    parser.add_argument("--binary_path", required=True, help="Path to the binary GPS data file.")
    parser.add_argument("--visualize", action="store_true", help="Visualize the processed GPS data on a (folium) map")

    args = parser.parse_args()

    print("Parsing database...")
    packets = read_database(args.db_path)
    print("Checking for missing database data based on record_ids...")
    check_missing_database_data(packets)

    print("Parsing the binary data...")
    df = read_binary_file(args.binary_path, packets)

    print("Filtering invalid timestamps...")
    df = filter_invalid_timestamps(df)

    print("Filtering GPS errors...")
    df = filter_gps_errors(df)

    print("Interpolating missing records...")
    df = interpolate_missing_records(df)

    print("Detecting roundabouts...")
    roundabouts_dataframe = detect_roundabouts(df)

    if args.visualize:
        print("Visualizing map...")
        visualize_map(df)
    else:
        print("Map visualization is disabled. Use --visualize argument to enable it.")

    print("Done! For further information check the logs folder in the root directory!")

if __name__ == "__main__":
    main()
