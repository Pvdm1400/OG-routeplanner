
import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
import os

OSRM_SERVER = "https://router.project-osrm.org"

# Tankstations als (Latitude, Longitude) tuples
tankstations = [
    (52.38042, 10.006417), (52.161625, 10.007915), (53.39059096, 10.04460454),
    (53.701913, 10.057361), (52.6091111111111, 10.07575), (53.63925, 10.0894444444444),
    (51.9472222222222, 10.1393611111111), (49.37658, 10.1993), (48.5438055555556, 10.3675555555556),
    (50.873632, 10.830234), (51.110276, 10.929985), (51.8109444444444, 10.9385833333333),
    (45.388855, 10.993261), (44.698492, 8.884370), (56.253201, 12.6255), (58.286241, 11.461953)
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
    d1 = geodesic((start[0], start[1]), (point[0], point[1])).km
    d2 = geodesic((point[0], point[1]), (end[0], end[1])).km
    d_total = geodesic((start[0], start[1]), (end[0], end[1])).km
    return abs((d1 + d2) - d_total) <= corridor_km

def build_route_with_filtered_tankstations(start, end, tankstations, interval_km=250):
    route = get_osrm_route([start, end])
    if not route:
        return []
    filtered_tanks = [ts for ts in tankstations if is_within_corridor(start, end, ts)]
    waypoints = [start]
    total_distance = 0
    last_point = route[0]
    for i in range(1, len(route)):
        curr_point = route[i]
        step_distance = geodesic((last_point[1], last_point[0]), (curr_point[1], curr_point[0])).km
        total_distance += step_distance
        if total_distance >= interval_km:
            if filtered_tanks:
                closest = min(filtered_tanks, key=lambda s: geodesic((curr_point[1], curr_point[0]), s).km)
                waypoints.append((closest[0], closest[1]))
            else:
                waypoints.append((curr_point[1], curr_point[0], "Geen tankstation in de buurt"))
            total_distance = 0
        last_point = curr_point
    waypoints.append(end)
    return waypoints

def mark_point_type(route, waypoints, tolerance=0.001):
    types = []
    for lon, lat in route:
        match = "Routepunt"
        for wp in waypoints:
            if len(wp) == 3 and wp[2] == "Geen tankstation in de buurt":
                wlat, wlon = wp[0], wp[1]
                label = wp[2]
            else:
                wlat, wlon = wp
                label = "Tankstation"
            if abs(lat - wlat) < tolerance and abs(lon - wlon) < tolerance:
                match = label
                break
        types.append(match)
    return types

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

# Streamlit interface
st.title("OG Routeplanner met Tankstations")

col1, col2 = st.columns(2)
with col1:
    start_lat = st.number_input("Start Latitude", value=59.3293)
    start_lon = st.number_input("Start Longitude", value=18.0686)
with col2:
    end_lat = st.number_input("Eind Latitude", value=50.8503)
    end_lon = st.number_input("Eind Longitude", value=4.3517)

route_name = st.text_input("Routenaam", value="Mijn Route")

if st.button("Genereer Route"):
    start = (start_lat, start_lon)
    end = (end_lat, end_lon)
    waypoints = build_route_with_filtered_tankstations(start, end, tankstations)
    route_coords = get_osrm_route([(wp[0], wp[1]) if isinstance(wp, tuple) else (wp[0], wp[1]) for wp in waypoints])
    if route_coords:
        df = pd.DataFrame(route_coords, columns=["Longitude", "Latitude"])
        df["Type"] = mark_point_type(route_coords, waypoints)
        df["Route"] = route_name
        st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
        st.dataframe(df)
        save_route_log(start, end, route_name)
        st.success("Route gegenereerd en opgeslagen!")
    else:
        st.error("Kon geen route genereren met OSRM.")
