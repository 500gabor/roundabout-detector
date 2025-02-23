import folium
import webbrowser
import os
from .utils import global_logger


def visualize_map(gdf):
    global_logger.info("Visualizing map using Folium!")

    coordinates = gdf[["latitude", "longitude"]].values

    m = folium.Map(location=[47.4979, 19.0402], zoom_start=12, tiles="cartodbdark_matter")
    folium.PolyLine(
        locations=coordinates,
        color="cyan",
        weight=3,
        opacity=0.8
    ).add_to(m)

    file_path = os.path.abspath("../folium_map.html")
    m.save(file_path)
    webbrowser.open(file_path)

    global_logger.info(f"Visalization complete! Saved map to: {file_path}")

