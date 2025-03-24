
import streamlit as st
import requests
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="OG Routeplanner", layout="wide")
st.image("Alleen spark.png", width=80)
st.title("OG Routeplanner")

# Gebruikersinstellingen
st.sidebar.header("Route-instellingen")
afstand_interval = st.sidebar.slider("Afstand tussen tankstations (km)", min_value=50, max_value=500, value=250, step=10)
max_afwijking = st.sidebar.slider("Maximale afwijking van route (km)", min_value=10, max_value=300, value=100, step=10)

# Ingebouwde lijst met tankstations
tankstations = [
    ("ADRIANO OLIVETTI SNC 13048", 45.38002021, 8.14634168),
    ("LUIGI GHERZI 15 28100", 454.54214523, 86.48874407),
    ("MEZZACAMPAGNA SNC 37135", 45.38885498, 109.93260597),
    ("Via Gramsci 45 15061", 44.69849229, 88.84370036),
    ("Korendreef  31", 0.00000052, 0.00000000),
    ("Osterstraße 90", 5.28505833, 8.05091667),
    ("An der alten Bundesstraße 210", 0.00000005, 0.00000008),
    ("An der B 167 4 (Finowfurt)", 0.00005285, 0.00136860),
    ("Bischheimer Straße 9", 0.00000005, 0.00000008),
    ("Bremer Straße 72 (Ostenburg)", 0.00005313, 0.00000823),
    ("Elmshorner Straße 36", 0.00000054, 0.00000010),
    ("Erftstraße 127 (Sindorf)", 0.00000509, 0.00000067),
    ("Esenser Straße 109", 0.00000005, 0.00000001),
    ("Friedenstraße 36", 0.00000005, 0.00000001),
    ("Hannoversche Heerstraße 44", 5.26091111, 0.00000001),
    ("Jeverstraße 9", 0.00000005, 0.00000008),
    ("Laatzener Straße  10 (Mittelfeld Messe)", 0.00000523, 0.00000010),
    ("Neuenkamper Straße 2-4", 0.00000051, 0.00000007),
    ("Oberrege 6", 0.00000053, 0.00000008),
    ("Oldenburger Straße 290a", 0.00000053, 0.00000008),
    ("Prinzessinweg 2 (Haarentor)", 0.00000001, 0.00000001),
    ("Schützenstraße 11", 0.00000052, 0.00000014),
    ("Spenglerstraße 2, Bernauer Straße, B 2 (Lindenberg)", 5.26081944, 0.00000001),
    ("Werler Straße 30", 0.00000052, 0.00000009),
    ("Winsener Straße 25 (Maschen)", 0.00005339, 0.00001004),
    ("Frankfurter Chaussee 68 (Fredersdorf)", 0.00000052, 0.00000014),
    ("Rudolf-Diesel-Straße 2 (Jübberde Remels Apen)", 0.00000005, 0.00000008),
    ("A. Plesmanlaan 1", 0.00000053, 0.00000007),
    ("Bornholmstraat 99", 0.00532043, 0.00006613),
    ("Böseler Straße 6", 0.00000005, 0.00000008),
    ("nan", 0.00000005, 7.16205556),
    ("nan", 5.31523333, 7.71202778),
    ("Beusichemseweg 58", 0.00000052, 0.00000001),
    ("Couwenhoekseweg 6", 0.00000052, 0.00000005),
    ("Emma Goldmanweg 4 (Katsbogten)", 0.00000052, 0.00000005),
    ("Groningerweg 58", 0.00000053, 0.00000006),
    ("Henri Blomjousstraat 1", 0.00000052, 0.00000005),
    ("Im Doorgrund 2", 0.00000005, 0.00000008),
    ("Kruisweg 471 (Schiphol)", 0.00000052, 0.00000005),
    ("Skoon 2", 0.00000052, 0.00000005),
    ("Stedinger Straße 6 (Bookholzberg)", 5.30891944, 8.52883333),
    ("Wasaweg  20", 0.00000053, 0.00000007),
    ("nan", 0.00004902, 0.00001095),
    ("Hauptstraße 138", 0.00000005, 0.00000008),
    ("nan", 4.75527778, 9.70163889),
    ("Blexersander Straße 2", 0.00000005, 0.00000085),
    ("Daimlerstraße 32", 0.00000049, 0.00000009),
    ("Oldenburger Straße 69", 0.00000053, 0.00000008),
    ("Siedlungsweg 2", 0.00000051, 0.00000011),
    ("Leher Straße 2a (Spaden)", 0.00000054, 0.00000009),
    ("Bedrijfsweg 2", 0.00000005, 0.00000005),
    ("Binckhorstlaan 100", 0.00000005, 0.00000004),
    ("Cornelis Douwesweg 15", 0.00000052, 0.00000005),
    ("Middelweg 3", 0.00000052, 0.00000005),
    ("Middenweg 100", 0.00000051, 0.00000006),
    ("A4", 0.00000052, 0.00000000),
    ("Fürstenwalder Straße 10c", 0.00000052, 0.00000014),
    ("Langenfelder Straße 105", 0.00000051, 0.00000007),
    ("Bahnhofstraße 40", 5.30913056, 7.39080556),
    ("Bremer Straße 55", 0.00000053, 0.00000001),
    ("Giflitzer Straße 12", 5.11326111, 9.12341667),
    ("Ostendorfer Straße 1", 0.00000053, 0.00000009),
    ("Industriestraat 1", 0.00000052, 0.00000005),
    ("Maaswijkweg 5", 0.00000005, 0.00000004),
    ("Vormerij 12", 0.00005229, 0.00674479),
    ("Burgemeester Grollemanweg 8", 0.00005296, 0.00065486),
    ("Changing Lane 10", 0.00000052, 0.00000005),
    ("Rijksstraatweg 124", 0.00000052, 0.00000000),
    ("Noorddijk 7", 0.00000051, 0.00000006),
    ("nan", 4.93587778, 6.71811111),
    ("nan", 0.00000051, 0.00000012),
    ("nan", 0.00000005, 0.00000001),
    ("Ammerlandallee 18-20", 0.00000053, 0.00000008),
    ("Berliner Straße 6", 0.00000005, 0.00000007),
    ("Binderslebener Landstraße 100", 0.00000005, 0.00000001),
    ("Erdinger Straße 145", 4.83841389, 1.17640833),
    ("Europa-Allee 4", 0.00000053, 0.00000006),
    ("Fahrenheitstraat 2", 0.00000053, 0.00000001),
    ("Große Rurstraße 100", 0.00000051, 0.00006353),
    ("Grüner Hof 5", 0.00000005, 7.86286111),
    ("Hamburger Straße 211", 0.00000005, 0.00000010),
    ("Heinsbergerweg 3a", 0.00000051, 0.00000006),
    ("Lathener Straße 1 - 3", 0.00000053, 0.00000007),
    ("Mainzer Straße 84", 0.00049643, 0.00836337),
    ("Martin-Luther-Straße 18", 0.00000051, 0.00000007),
    ("Oldenburger Damm 12", 5.34845278, 8.02744444),
    ("Oldenburger Straße 14", 0.00000053, 0.00000008),
    ("Oldenburger Straße 141", 0.00005324, 0.00000820),
    ("Oranienbaumer Chaussee 40 (Mildensee)", 0.00000005, 0.00000001),
    ("Podbielskistraße 216 (List)", 0.00000001, 9.78091667),
    ("Schiffmühler Straße 2", 0.00000005, 0.00000001),
    ("Schwieberdinger Straße 133", 0.00000000, 0.00000009),
    ("Uerdinger Straße 8", 0.00000001, 0.00000007),
    ("Vahrenwalder Straße 138 (Vahrenwald)", 0.00000052, 0.00000010),
    ("Wachbacher Straße 100", 4.94763889, 9.77155556),
    ("Weimarische Straße 36", 0.00000005, 1.10545833),
    ("Werner-Kammann-Straße 3-7", 0.00000005, 0.00000009),
    ("nan", 0.00000050, 0.00000001),
    ("Am Zainer Berg 2 (Rhüden)", 5.19472222, 1.01393611),
    ("nan", 0.00000053, 0.00000008),
    ("Benjamin Franklinstraat 2", 0.00000005, 0.00000007),
    ("Ossebroeken 8", 0.00052859, 0.00006495),
    ("Stephensonstraat 63", 0.00000053, 0.00000007),
    ("Stettinweg 22", 0.00000053, 0.00000007),
    ("Wethouder Kuijersstraat 2", 0.00000053, 0.00000006),
    ("Morseweg 1c", 0.00000053, 0.00000006),
    ("Kemnather Straße 78", 0.00000050, 0.00000012),
    ("Ziegelhütter Weg 14-16", 0.00000051, 0.00000009),
    ("Biltseweg 2", 0.00000052, 0.00000001),
    ("Bremer Straße 69", 5.24390833, 9.58880556),
    ("Hans-Mess-Straße 2", 0.00502241, 0.00085805),
    ("Industriestraße 29", 0.00000005, 0.00000012),
    ("Steinbrüchenstraße 1", 0.00000005, 0.00000001),
    ("Bünder Straße 184 (Lippinghausen)", 0.00521491, 0.00865002),
    ("nan", 0.05306024, 0.00916493),
    ("Posthalterweg 10 (Wechloy)", 0.00000005, 0.00000008),
    ("Gottlieb-Daimler-Straße 2c (Harber)", 0.00005300, 0.00000992),
    ("Otto-Hahn-Straße 5", 0.00000005, 0.00000001),
    ("Hagener Straße 110-114", 0.00513251, 0.00073529),
    ("Galjoenweg 17", 0.00000005, 0.00000006),
    ("Davenstedter Straße 128a (Lindener Hafen)", 0.00000005, 0.00000097),
    ("De Flinesstraat 9 (Duivendrecht)", 0.00000052, 0.00000005),
    ("Industriestraße 10", 5.21914722, 8.35427778),
    ("nan", 0.00000053, 0.00000007),
    ("nan", 0.00000005, 0.00000000),
    ("nan", 0.00000050, 0.00000008),
    ("nan", 0.00050094, 0.00090496),
    ("nan", 5.18109444, 1.09385833),
    ("nan", 0.00000052, 0.00000012),
    ("A.J. Romijnweg  10", 0.00000005, 0.00000001),
    ("Alehögsvägen 2", 0.00000057, 0.00000015),
    ("Antenngatan 2 (Marconimotet)", 0.00000006, 0.00000001),
    ("Argongatan 30 (Åbro Industriområde)", 0.00000006, 0.00000001),
    ("Atoomweg 40", 0.00000005, 0.00000001),
    ("Australiëhavenweg 21", 0.00000005, 0.00000005),
    ("Axel Odhners Gata 60 (Högsbo)", 0.00000006, 0.00000001),
    ("Barrier Straße 33", 0.00000005, 0.00000001),
    ("Bergerstraße 97", 0.00000053, 0.00000014),
    ("Beurtvaart 3", 0.00000053, 0.00000006),
    ("Bockängsgatan 3", 0.00000058, 0.00000015),
    ("Borgens gata 1", 0.00000058, 0.00000013),
    ("Brodalsvägen 6", 0.00000058, 0.00000012),
    ("Brofästet Öland 3", 0.00000057, 0.00016490),
    ("Brogårdsgatan 22", 0.00000057, 0.00000015),
    ("Bultgatan 41 (Rollsbo industriområde)", 0.00000006, 0.00000000),
    ("De Stuwdam 5", 0.00000052, 0.00000005),
    ("Deltavägen 13", 0.00000006, 0.00000001),
    ("Dordrechtweg 11", 0.00000052, 0.00000006),
    ("Drottningholmsvägen 490 (Bromma)", 0.00000059, 0.00000018),
    ("Florynwei  5", 0.00000053, 0.00000006),
    ("Förrådsvägen 1", 0.00000058, 0.00000011),
    ("Generatorstraat 18", 0.00000052, 0.00000005),
    ("Gjutjärnsgatan 1 (Ringön)", 0.00000006, 0.00000001),
    ("Göteborgsvägen 2a", 0.00000001, 0.00000000),
    ("Hammarsmedsgatan 27", 0.00000587, 0.00000014),
    ("Hangarvägen (Härryda)", 0.00000058, 0.00000012),
    ("Hantverksgatan 34 (Inlag)", 0.05747849, 0.00001208),
    ("Hjortshögsvägen 7", 0.00005607, 0.00127668),
    ("Hoendiep 270", 0.00000053, 0.00000006),
    ("Importgatan 4 (Hisings Backa)", 0.00005775, 0.00119925),
    ("Industriewei 25", 0.00000053, 0.00000006),
    ("Johannesbergsvägen 1", 0.00000006, 0.00000001),
    ("Kraftgatan 11", 0.00000058, 0.00000014),
    ("Kungsparksvägen 1", 0.00000006, 0.00000001),
    ("Monteringsvägen 2 (Volvo Sörred)", 0.00000001, 0.00000001),
    ("Nudepark 200", 0.00000052, 0.00000001),
    ("Oljevägen 1", 0.00000006, 0.00000001),
    ("Overijsselsestraatweg 1a", 0.00000001, 0.00000006),
    ("Petter Jönssons Väg 4", 0.00000058, 0.00000015),
    ("Pluto 3", 0.00005298, 0.00005938),
    ("Ramsåsa 908", 0.00555601, 0.00013912),
    ("Regementsgatan  22", 0.00000058, 0.00000013),
    ("Ribbingsbergsgatan 5", 0.00000056, 0.00000014),
    ("Robert-Koch-Straße 4", 0.00528531, 0.09691328),
    ("Sankt Sigfridsgatan 91 (Kallebäck)", 0.00000006, 0.00000001),
    ("Sikkel 22", 0.00000053, 0.00000007),
    ("Slängom", 0.00000006, 0.00000001),
    ("Spadegatan 22 (Angered)", 0.00000058, 0.00000000),
    ("Stettiner Straße 25", 0.00504353, 0.00749242),
    ("Susvindsvägen 21", 0.00000001, 0.00000001),
    ("Sydhamnsgatan 12", 0.00000006, 0.00000001),
    ("Tallskogsvägen", 0.00000585, 0.00001314),
    ("Tradenvägen 6 (Håby gård)", 0.00000058, 0.00000012),
    ("Vallenvägen 5 (Stora Höga)", 0.00000058, 0.00000012),
    ("Vänersborgsvägen - Wallentinsvägen", 0.00000058, 0.00000013),
    ("Vasavägen 1", 0.00000006, 0.00000001),
    ("Veldkampsweg 26", 0.00000524, 0.00000007),
    ("Vilangatan", 0.00000006, 0.00000001),
    ("Warodells väg 3", 0.00000058, 0.00001356),
    ("Westfalenstraße  10", 0.00005133, 0.00069783),
    ("Alte Heerstrasse 1 (Einum)", 0.00000052, 0.00000010),
    ("Düsseldorfer Landstraße 424 (Huckingen)", 0.00000005, 0.00000007),
    ("Grevesmühlener Straße  6", 0.00000054, 0.00000112),
    ("Harburger Straße 18", 0.00000054, 0.00000009),
    ("Lornsenstraße 142", 0.00000054, 0.00000010),
    ("Mielestraße 20", 0.00000005, 0.00000010),
    ("Rolfinckstraße 48 (Wellingsbüttel)", 0.00000005, 1.00894444),
    ("Segeberger Chaussee 345", 0.00000054, 0.00000010),
    ("Viktoriastraße 22 - 24", 0.00000052, 0.00000009),
    ("Wanderslebener Straße 24 (Mühlberg)", 0.00000051, 0.00000011),
    ("Nobelstraat 6", 0.00000052, 0.00000006),
    ("Nadorster Straße 253 (Nadorst)", 0.00005316, 0.00822524),
    ("nan", 0.00000051, 0.00000013),
    ("Raiffeisenstraße 18", 5.34573333, 7.49766667),
    ("nan", 4.85438056, 1.03675556),
    ("Ängelholmsvägen 38", 0.00000006, 0.00000001),
    ("Skördevägen 2 (Lerberget)", 5.61808014, 1.25639000),
    ("Osterholzer Heerstraße 161 (Osterholz)", 5.30576111, 0.00000001),
    ("Europaweg 1", 0.00531673, 0.00068662),
    ("Vossenkamp 8", 0.00000053, 0.00000006),
    ("nan", 0.00000005, 0.00000001),
    ("Berliner Straße 1-3 (Dorum)", 0.00000054, 0.00000086),
    ("Celler Straße  58", 0.00000053, 0.00000010),
    ("Delmenhorster Straße 12", 0.00000005, 0.00000008),
    ("Hindenburgstraße 1", 0.00053374, 0.00009008),
    ("Industriestraße 2", 0.00000053, 0.00000009),
    ("Raiffeisenstraße 10 (Bad Bederkesa)", 0.00000054, 0.00000009),
    ("Stader Straße 40", 5.36811111, 9.17913889),
    ("Warsteiner Straße 41", 5.13604722, 8.28661111),
    ("Werderstraße 3-4", 0.00000005, 0.00000001),
    ("Wildeshauser Landstraße 60", 0.00000053, 0.00000009),
    ("Henleinstraße 1", 0.00000053, 0.00000009),
    ("['s-Hertogenbosch]", 0.00000052, 0.00000005),
    ("Anthony Fokkerweg 8", 0.00000052, 0.00000005),
    ("De Striptekenaar 83", 0.00000052, 0.00000005),
    ("Dijkje 20", 0.00000005, 0.00000005),
    ("Haardijk 3", 0.00000005, 0.00000007),
    ("Ookmeerweg 501", 0.00000052, 0.00000005),
    ("Parkweg 98", 0.00000052, 0.00000007),
    ("Randweg 18 ( )", 0.00000053, 0.00000006),
    ("Rondweg 3", 0.00000052, 0.00000007),
    ("Sögeler Straße 9", 0.00005285, 0.00000767),
    ("Chausseestraße 1", 0.00000005, 0.00000136),
    ("Ruhlebener Straße 1a (Spandau)", 0.00000053, 0.00000013),
    ("Bahnhofstraße 2", 5.29684167, 7.34886111),
    ("Bassumer Straße 83", 0.00000053, 0.00000009),
    ("Emder Straße 33 (Georgsheil)", 0.00000005, 0.00000001),
    ("Gernröder Chaussee 1", 5.17716389, 1.11404167),
    ("Mindener Straße 2a", 0.00000005, 0.00000009),
    ("Monschauer Straße 69", 5.07932222, 6.47052778),
    ("Schönauer Straße 113 (Großzschocher)", 5.13106944, 1.23088333),
    ("Venloer Straße 1", 5.15201944, 6.31011111),
    ("Westersteder Straße 14a (Zetel)", 0.00000534, 0.00000795),
    (" Marconistraat 17", 0.00000052, 0.00000006),
    ("Kieler Straße 196 - 198 (Zentrum)", 5.40889444, 9.98669444),
    ("Cloppenburger Straße 224 (Kreyenbrück)", 0.00000053, 0.00000008),
    ("De Wissel 2", 0.00000053, 0.00000006),
    ("Dolderweg 48", 0.00000053, 0.00000006),
    ("Geraldadrift 2", 0.00000053, 0.00000007),
    ("Havenweg 23", 0.00000052, 0.00000005),
    ("Kissel 43", 0.00000051, 0.00000001),
    ("Okkenbroekstraat 19", 0.00000052, 0.00000006),
    ("Parkweg 85", 0.00000052, 0.00000005),
    ("Raalterweg 56", 0.00000052, 0.00000006),
    ("Sint Bonifaciuslaan 83", 0.00000051, 0.00000006),
    ("Stationsweg 24", 0.00000053, 0.00000006),
    ("Wijheseweg 45", 0.00000052, 0.00000006),
    ("Piet Van Donkplein 3", 0.00005225, 0.00006207),
    ("Schiedamsedijk 12", 0.00000052, 0.00000004),
    ("Seggelant-Zuid 1", 0.00000052, 0.00000004),
    ("nan", 0.00000052, 0.00000009),
    ("Cuxhavener Straße 31", 0.00000054, 0.00000009),
    ("Midslanderhoofdweg 5 (Midsland)", 0.00000053, 0.00000005),
    ("Uterwei 20", 0.00000053, 0.00000006),
    ("Lozerlaan 4 (De Uithof)", 0.00000052, 0.00000004),
    ("Rijksstraatweg 82", 0.00005251, 0.00000465),
    ("de Bolder 71", 0.00000053, 0.00000006),
    ("Jupiterweg 7", 0.00000053, 0.00000006),
    ("Transportweg 24", 0.00000052, 0.00000005),
    ("Bremer Straße 46", 0.00000001, 0.00000009),
    ("Hildesheimer Straße 407 (Wülfel)", 5.23264167, 9.78166667),
]


# Start- en eindlocatie invoer
st.sidebar.header("Routepunten")
start_loc = st.sidebar.text_input("Startlocatie (bijv. Amsterdam)")
end_loc = st.sidebar.text_input("Eindlocatie (bijv. Berlijn)")

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

        # Voeg start en eindpunt toe
        folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(end_coords, tooltip="Eind", icon=folium.Icon(color="red")).add_to(m)

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
