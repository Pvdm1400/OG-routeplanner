
import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Titel en header
st.set_page_config(page_title="OG Routeplanner", layout="wide")

# Groene titelbalk
st.title("OG Routeplanner")
st.image("https://www.ogcleanfuels.com/logo.png", width=150)
st.markdown("### REFUELING LOCATIONS
An OG refueling location is always nearby!")

# Gebruikersinstellingen en layout
col1, col2 = st.columns([1, 2])  # Split de pagina in twee kolommen

with col1:
    st.sidebar.header("Route-instellingen")
    afstand_interval = st.slider("Afstand tussen tankstations (km)", min_value=50, max_value=500, value=250, step=10)
    max_afwijking = st.slider("Maximale afwijking van route (km)", min_value=10, max_value=300, value=100, step=10)

    st.sidebar.header("Routepunten")
    start_loc = st.sidebar.text_input("Startlocatie (bijv. Amsterdam)")
    end_loc = st.sidebar.text_input("Eindlocatie (bijv. Berlijn)")

with col2:
    # Ingebouwde lijst met tankstations
    tankstations = [
        ("ADRIANO OLIVETTI SNC 13048", 45.38002020650739, 8.14634168147584),
        ("LUIGI GHERZI 15 28100", 45.454214522946366, 8.648874406509199),
        ("MEZZACAMPAGNA SNC 37135", 45.38885497663997, 10.993260597366502),
        ("Via Gramsci 45 15061", 44.69849229353388, 8.884370036245732),
        ("Korendreef  31", 51.750893, 4.16553),
        ("Osterstraße 90", 52.8505833333333, 8.05091666666667),
        ("An der alten Bundesstraße 210", 53.56057, 7.915976),
        ("An der B 167 4 (Finowfurt)", 52.84995142, 13.6860187738),
        ("Bischheimer Straße 9", 49.66834, 8.019837),
        ("Bremer Straße 72 (Ostenburg)", 53.12928341, 8.22720408),
        ("Elmshorner Straße 36", 53.905796, 9.507996),
        ("Erftstraße 127 (Sindorf)", 50.9115278, 6.6834722),
        ("Esenser Straße 109", 53.48224, 7.49042),
        ("Friedenstraße 36", 52.33592, 14.07347),
        ("Hannoversche Heerstraße 44", 52.6091111111111, 10.07575),
        ("Jeverstraße 9", 53.57615, 7.792493),
        ("Laatzener Straße  10 (Mittelfeld Messe)", 52.3231389, 9.813944),
        ("Neuenkamper Straße 2-4", 51.177067, 7.211746),
        ("Oberrege 6", 53.235475, 8.455755),
        ("Oldenburger Straße 290a", 53.056872, 8.199678),
        ("Prinzessinweg 2 (Haarentor)", 53.1435, 8.19194),
        ("Schützenstraße 11", 52.395114, 13.533889),
        ("Spenglerstraße 2, Bernauer Straße, B 2", 52.5175, 13.401944)
    ]

    geolocator = Nominatim(user_agent="og-routeplanner")

    def geocode(loc):
        try:
            location = geolocator.geocode(loc)
            return (location.latitude, location.longitude)
        except:
            return None

    if start_loc and end_loc:
        start_coords = geocode(start_loc)
        end_coords = geocode(end_loc)

        if start_coords and end_coords:
            # Bereken afstand
            route_afstand = geodesic(start_coords, end_coords).km

            # Filter tankstations binnen corridor
            def is_within_corridor(start, end, point, corridor_km):
                d1 = geodesic(start, (point[1], point[2])).km
                d2 = geodesic((point[1], point[2]), end).km
                d_total = geodesic(start, end).km
                return abs((d1 + d2) - d_total) <= corridor_km

            filtered_stations = [ts for ts in tankstations if is_within_corridor(start_coords, end_coords, ts, max_afwijking)]

            # Bouw folium-kaart
            m = folium.Map(location=start_coords, zoom_start=6)

            # Voeg start en eindpunt toe met groene lijn
            folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(end_coords, tooltip="Eind", icon=folium.Icon(color="green")).add_to(m)
            folium.PolyLine([start_coords, end_coords], color="green", weight=3, opacity=1).add_to(m)

            # Voeg tankstation-markers toe
            for name, lat, lon in filtered_stations:
                folium.Marker(
                    location=(lat, lon),
                    tooltip=name,
                    icon=folium.Icon(color="blue", icon="tint", prefix="fa")
                ).add_to(m)

            # Toon kaart
            st_folium(m, width=900, height=600)

            # Toon afstand
            st.markdown(f"### Totale afstand tussen start en eindpunt: **{route_afstand:.2f} km**")
        else:
            st.error("Start of eindlocatie kon niet worden gevonden.")
    else:
        st.info("Vul een start- en eindlocatie in om de route te berekenen.")
