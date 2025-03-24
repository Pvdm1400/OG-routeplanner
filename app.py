
import streamlit as st
st.image("Alleen spark.png", width=80)

import requests
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

OSRM_SERVER = "https://router.project-osrm.org"

# Tankstations als ("Naam", Latitude, Longitude) tuples
tankstations = [
    ("Tankstation A", 52.38042, 10.006417),
    ("Tankstation B", 52.161625, 10.007915),
    ("Tankstation C", 53.39059096, 10.04460454),
    ("Tankstation D", 53.701913, 10.057361),
    ("Tankstation E", 52.6091111111111, 10.07575)
]

def get_osrm_route(waypoints):
    waypoint_str = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
    url = f"{OSRM_SERVER}/route/v1/driving/{waypoint_str}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    if 'routes' not in data or not data['routes']:
        return []
    return data['routes'][0]['geometry']['coordinates']

def is_within_corridor(start, end, point, corridor_km=100):
    d1 = geodesic((start[0], start[1]), (point[1], point[2])).km
    d2 = geodesic((point[1], point[2]), (end[0], end[1])).km
    d_total = geodesic((start[0], start[1]), (end[0], end[1])).km
    return abs((d1 + d2) - d_total) <= corridor_km

def build_route_with_filtered_tankstations(start, end, tankstations, interval_km=250):
    route = get_osrm_route([start, end])
    if not route:
        return [], []
    filtered_tanks = [ts for ts in tankstations if is_within_corridor(start, end, ts)]
    waypoints = [start]
    used_stations = []
    total_distance = 0
    last_point = route[0]
    for i in range(1, len(route)):
        curr_point = route[i]
        step_distance = geodesic((last_point[1], last_point[0]), (curr_point[1], curr_point[0])).km
        total_distance += step_distance
        if total_distance >= interval_km:
            if filtered_tanks:
                closest = min(filtered_tanks, key=lambda s: geodesic((curr_point[1], curr_point[0]), (s[1], s[2])).km)
                waypoints.append((closest[1], closest[2]))
                used_stations.append(closest)
            else:
                used_stations.append(("Geen tankstation in de buurt", curr_point[1], curr_point[0]))
                waypoints.append((curr_point[1], curr_point[0]))
            total_distance = 0
        last_point = curr_point
    waypoints.append(end)
    return waypoints, used_stations

def geocode_address(address):
    geolocator = Nominatim(user_agent="streamlit-routeplanner")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# Streamlit UI
st.title("OG Routeplanner")

start_address = st.text_input("Startadres", value="Stockholm, Zweden")
end_address = st.text_input("Eindadres", value="Brussel, België")
route_name = st.text_input("Routenaam", value="Mijn Route")

if st.button("Genereer Route"):
    start = geocode_address(start_address)
    end = geocode_address(end_address)

    if not start or not end:
        st.error("Kon één van de adressen niet vinden.")
    else:
        waypoints, used_stations = build_route_with_filtered_tankstations(start, end, tankstations)
        route_coords = get_osrm_route([(wp[0], wp[1]) for wp in waypoints])
        if route_coords:
            df = pd.DataFrame(route_coords, columns=["Longitude", "Latitude"])
            df["Route"] = route_name
            st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
            st.subheader("Tankstations op de route")
            for i, (name, _, _) in enumerate(used_stations, 1):
                st.markdown(f"🛢️ **Tankstation {i}:** {name}")
        else:
            st.error("Kon geen route genereren met OSRM.")

import folium
from folium import Map, Marker, CustomIcon, Popup
import os

# Maak een kaart (voorbeeld met centrum op eerste tankstation)
m = Map(location=[tankstations[0][1], tankstations[0][2]], zoom_start=7)

# Gebruik absoluut pad voor het icoon zodat het werkt in Streamlit
icon_path = os.path.abspath("Alleen spark.png")

# Voeg markers toe met afbeelding als icoon

# Gebruik base64 data URL als zichtbaar icoon
icon = folium.CustomIcon("data:image/png;base64,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", icon_size=(50, 50))

for name, lat, lon in tankstations:
    Marker(
        location=(lat, lon),
        icon=icon,
        popup=Popup(name)
    ).add_to(m)

# Toon de kaart in Streamlit
from streamlit_folium import st_folium
st_folium(m, width=700, height=500)
