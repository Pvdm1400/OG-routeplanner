
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
icon = CustomIcon(icon_path, icon_size=(30, 30))

# Voeg markers toe met afbeelding als icoon
for name, lat, lon in tankstations:
    Marker(
        location=(lat, lon),
        icon=icon,
        popup=Popup(name)
    ).add_to(m)

# Toon de kaart in Streamlit
from streamlit_folium import st_folium
st_folium(m, width=700, height=500)
