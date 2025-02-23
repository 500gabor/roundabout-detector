import folium
import numpy as np
import webbrowser
import os
from src.roundabout_detector.utils import global_logger


def visualize_map(gdf):
    try:
        global_logger.info("Visualizing map using Folium!")

        coordinates = gdf[["latitude", "longitude"]].values
        center_lat, center_lon = np.mean(coordinates, axis=0)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="cartodbdark_matter")
        folium.PolyLine(
            locations=coordinates,
            color="cyan",
            weight=3,
            opacity=0.8
        ).add_to(m)

        file_path = os.path.abspath("../folium_map.html")
        m.save(file_path)
        webbrowser.open(file_path)

        global_logger.info(f"Visalization complete! Saved map to: {file_path}.")
        global_logger.info("-" * 50)
    except Exception as error:
        global_logger.error(f"[ERROR] Failed map visualization. Error: {error}")

