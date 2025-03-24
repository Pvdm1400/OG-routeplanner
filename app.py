
import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os

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
                used_stations.append(closest[0])
            else:
                used_stations.append("Geen tankstation in de buurt")
                waypoints.append((curr_point[1], curr_point[0]))
            total_distance = 0
        last_point = curr_point
    waypoints.append(end)
    return waypoints, used_stations

def save_route_log(start, end, route_name):
    log_entry = pd.DataFrame([{
        "Route": route_name,
        "Start_Lat": start[0],
        "Start_Lon": start[1],
        "End_Lat": end[0],
        "End_Lon": end[1]
    }])
    log_file = "route_log.csv"
    if os.path.exists(log_file):
        old_log = pd.read_csv(log_file)
        full_log = pd.concat([old_log, log_entry], ignore_index=True)
    else:
        full_log = log_entry
    full_log.to_csv(log_file, index=False)

def geocode_address(address):
    geolocator = Nominatim(user_agent="streamlit-routeplanner")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# Streamlit interface
st.title("OG Routeplanner met Tankstations")

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
            st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
            st.subheader("Tankstations op de route")
            for i, station in enumerate(used_stations, 1):
                st.markdown(f"🛢️ **Tankstation {i}:** {station}")
            save_route_log(start, end, route_name)
        else:
            st.error("Kon geen route genereren met OSRM.")
