import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

OSRM_SERVER = "https://router.project-osrm.org"

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
    ("Spenglerstraße 2, Bernauer Straße, B 2 (Lindenberg)", 52.6081944444444, 13.52875),
    ("Werler Straße 30", 52.084475, 8.736217),
    ("Winsener Straße 25 (Maschen)", 53.39059096, 10.04460454),
    ("Frankfurter Chaussee 68 (Fredersdorf)", 52.499652, 13.743842),
    ("Rudolf-Diesel-Straße 2 (Jübberde Remels Apen)", 53.26297, 7.756261),
    ("A. Plesmanlaan 1", 53.176219, 6.733337),
    ("Bornholmstraat 99", 53.2043178635, 6.612641631),
    ("Böseler Straße 6", 52.96187, 8.026265),
    ("nan", 51.77875, 7.16205555555556),
    ("nan", 53.1523333333333, 7.71202777777778),
    ("Beusichemseweg 58", 52.004804, 5.21631),
    ("Couwenhoekseweg 6", 51.937013, 4.592922),
    ("Emma Goldmanweg 4 (Katsbogten)", 51.537532, 5.040958),
    ("Groningerweg 58", 53.167164, 6.496736),
    ("Henri Blomjousstraat 1", 51.584174, 5.057983),
    ("Im Doorgrund 2", 53.17015, 7.998636),
    ("Kruisweg 471 (Schiphol)", 52.286843, 4.727935),
    ("Skoon 2", 52.432218, 4.875834),
    ("Stedinger Straße 6 (Bookholzberg)", 53.0891944444444, 8.52883333333333),
    ("Wasaweg  20", 53.215244, 6.613511),
    ("nan", 49.01990844, 10.95113754),
    ("Hauptstraße 138", 53.41759, 7.739631),
    ("nan", 47.5527777777778, 9.70163888888889),
    ("Blexersander Straße 2", 53.50733, 8.4948055),
    ("Daimlerstraße 32", 48.603166, 8.870917),
    ("Oldenburger Straße 69", 52.737108, 8.285123),
    ("Siedlungsweg 2", 51.110276, 10.929985),
    ("Leher Straße 2a (Spaden)", 53.571171, 8.622775),
    ("Bedrijfsweg 2", 52.09607, 4.945655),
    ("Binckhorstlaan 100", 52.07174, 4.335824),
    ("Cornelis Douwesweg 15", 52.415359, 4.874565),
    ("Middelweg 3", 51.844831, 4.519428),
    ("Middenweg 100", 50.985302, 5.843929),
    ("A4", 52.261493, 4.68724),
    ("Fürstenwalder Straße 10c", 52.182064, 14.242636),
    ("Langenfelder Straße 105", 51.066226, 6.924465),
    ("Bahnhofstraße 40", 53.0913055555556, 7.39080555555556),
    ("Bremer Straße 55", 53.112635, 9.22681),
    ("Giflitzer Straße 12", 51.1326111111111, 9.12341666666667),
    ("Ostendorfer Straße 1", 53.219486, 8.935207),
    ("Industriestraat 1", 52.011277, 4.693377),
    ("Maaswijkweg 5", 51.84198, 4.347907),
    ("Vormerij 12", 52.28670629, 6.74478852473),
    ("Burgemeester Grollemanweg 8", 52.95947712, 6.5486321837),
    ("Changing Lane 10", 52.270314, 4.692568),
    ("Rijksstraatweg 124", 51.751246, 4.63926),
    ("Noorddijk 7", 51.466612, 5.688338),
    ("nan", 49.3587777777778, 6.71811111111111),
    ("nan", 51.144573, 11.834173),
    ("nan", 52.70465, 13.44013),
    ("Ammerlandallee 18-20", 53.251945, 7.932015),
    ("Berliner Straße 6", 51.29363, 7.289787),
    ("Binderslebener Landstraße 100", 50.97213, 10.97484),
    ("Erdinger Straße 145", 48.3841388888889, 11.7640833333333),
    ("Europa-Allee 4", 52.542936, 5.919186),
    ("Fahrenheitstraat 2", 53.182238, 5.46097),
    ("Große Rurstraße 100", 50.920081, 6.353367019),
    ("Grüner Hof 5", 53.02425, 7.86286111111111),
    ("Hamburger Straße 211", 53.74818, 9.694082),
    ("Heinsbergerweg 3a", 51.155393, 6.006385),
    ("Lathener Straße 1 - 3", 52.705282, 7.296353),
    ("Mainzer Straße 84", 49.642790997, 8.36337221285),
    ("Martin-Luther-Straße 18", 51.398748, 7.178095),
    ("Oldenburger Damm 12", 53.4845277777778, 8.02744444444444),
    ("Oldenburger Straße 14", 53.391638, 8.136491),
    ("Oldenburger Straße 141", 53.23668608, 8.20006013),
    ("Oranienbaumer Chaussee 40 (Mildensee)", 51.82499, 12.30073),
    ("Podbielskistraße 216 (List)", 52.3995, 9.78091666666667),
    ("Schiffmühler Straße 2", 52.79053, 14.04639),
    ("Schwieberdinger Straße 133", 48.8898, 9.160853),
    ("Uerdinger Straße 8", 51.3034, 6.671233),
    ("Vahrenwalder Straße 138 (Vahrenwald)", 52.397528, 9.736694),
    ("Wachbacher Straße 100", 49.4763888888889, 9.77155555555556),
    ("Weimarische Straße 36", 50.97375, 11.0545833333333),
    ("Werner-Kammann-Straße 3-7", 53.86635, 8.696526),
    ("nan", 50.114512, 8.61725),
    ("Am Zainer Berg 2 (Rhüden)", 51.9472222222222, 10.1393611111111),
    ("nan", 52.664354, 8.256793),
    ("Benjamin Franklinstraat 2", 52.35916, 6.512449),
    ("Ossebroeken 8", 52.859074945, 6.495129228),
    ("Stephensonstraat 63", 52.728889, 6.521828),
    ("Stettinweg 22", 53.220582, 6.602814),
    ("Wethouder Kuijersstraat 2", 52.631537, 6.212359),
    ("Morseweg 1c", 53.187406, 5.755853),
    ("Kemnather Straße 78", 50.033676, 11.989554),
    ("Ziegelhütter Weg 14-16", 51.283187, 8.862887),
    ("Biltseweg 2", 52.173667, 5.24636),
    ("Bremer Straße 69", 52.4390833333333, 9.58880555555556),
    ("Hans-Mess-Straße 2", 50.2241001665, 8.5805411038),
    ("Industriestraße 29", 50.54927, 11.789001),
    ("Steinbrüchenstraße 1", 50.96672, 11.25742),
    ("Bünder Straße 184 (Lippinghausen)", 52.1491387799, 8.65002118326),
    ("nan", 53.06023636928, 9.16493268831),
    ("Posthalterweg 10 (Wechloy)", 53.15943, 8.172347),
    ("Gottlieb-Daimler-Straße 2c (Harber)", 52.99676157, 9.92126584),
    ("Otto-Hahn-Straße 5", 52.82889, 8.11742),
    ("Hagener Straße 110-114", 51.3251138375, 7.3529331245),
    ("Galjoenweg 17", 50.87641, 5.705766),
    ("Davenstedter Straße 128a (Lindener Hafen)", 52.36544, 9.6900278),
    ("De Flinesstraat 9 (Duivendrecht)", 52.324954, 4.925004),
    ("Industriestraße 10", 52.1914722222222, 8.35427777777778),
    ("nan", 53.220329, 7.474366),
    ("nan", 49.37658, 10.1993),
    ("nan", 49.975596, 8.024672),
    ("nan", 50.094005576, 9.0495923987),
    ("nan", 51.8109444444444, 10.9385833333333),
    ("nan", 52.257729, 11.844004),
    ("A.J. Romijnweg  10", 53.13488, 7.05049),
    ("Alehögsvägen 2", 57.383421, 14.658687),
    ("Antenngatan 2 (Marconimotet)", 57.65942, 11.93295),
    ("Argongatan 30 (Åbro Industriområde)", 57.64175, 12.00772),
    ("Atoomweg 40", 52.10532, 5.06719),
    ("Australiëhavenweg 21", 52.39996, 4.795264),
    ("Axel Odhners Gata 60 (Högsbo)", 57.65061, 11.95224),
    ("Barrier Straße 33", 52.93144, 8.82531),
    ("Bergerstraße 97", 52.835972, 13.811128),
    ("Beurtvaart 3", 53.320804, 6.019134),
    ("Bockängsgatan 3", 57.650627, 14.738195),
    ("Borgens gata 1", 57.930801, 12.560001),
    ("Brodalsvägen 6", 57.742783, 12.127561),
    ("Brofästet Öland 3", 56.665372, 16.490252524),
    ("Brogårdsgatan 22", 57.413693, 15.083613),
    ("Bultgatan 41 (Rollsbo industriområde)", 57.88082, 11.9439),
    ("De Stuwdam 5", 52.168042, 5.432304),
    ("Deltavägen 13", 57.72848, 11.95476),
    ("Dordrechtweg 11", 52.248439, 6.181199),
    ("Drottningholmsvägen 490 (Bromma)", 59.337762, 17.934343),
    ("Florynwei  5", 53.205037, 5.984536),
    ("Förrådsvägen 1", 58.286241, 11.461953),
    ("Generatorstraat 18", 52.394434, 4.851491),
    ("Gjutjärnsgatan 1 (Ringön)", 57.72009, 11.96297),
    ("Göteborgsvägen 2a", 57.7639, 12.2594),
    ("Hammarsmedsgatan 27", 58.6784104, 13.820191),
    ("Hangarvägen (Härryda)", 57.673074, 12.300632),
    ("Hantverksgatan 34 (Inlag)", 57.47849019699, 12.08231532),
    ("Hjortshögsvägen 7", 56.06527923, 12.7667509757),
    ("Hoendiep 270", 53.214386, 6.492455),
    ("Importgatan 4 (Hisings Backa)", 57.74757535, 11.9924708334),
    ("Industriewei 25", 52.966524, 5.815859),
    ("Johannesbergsvägen 1", 58.35541, 12.31506),
    ("Kraftgatan 11", 57.747662, 14.163162),
    ("Kungsparksvägen 1", 57.50996, 12.06621),
    ("Monteringsvägen 2 (Volvo Sörred)", 57.7133, 11.84243),
    ("Nudepark 200", 51.960387, 5.64495),
    ("Oljevägen 1", 58.39289, 13.87718),
    ("Overijsselsestraatweg 1a", 53.1073, 5.783931),
    ("Petter Jönssons Väg 4", 57.676224, 14.694648),
    ("Pluto 3", 52.97605227, 5.937511449),
    ("Ramsåsa 908", 55.5600923446, 13.912333685),
    ("Regementsgatan  22", 57.715885, 12.917635),
    ("Ribbingsbergsgatan 5", 55.545217, 14.335263),
    ("Robert-Koch-Straße 4", 52.8530625009, 9.691328306979),
    ("Sankt Sigfridsgatan 91 (Kallebäck)", 57.68968, 12.00471),
    ("Sikkel 22", 53.321455, 6.882426),
    ("Slängom", 58.35423, 11.91448),
    ("Spadegatan 22 (Angered)", 57.788889, 12.0454),
    ("Stettiner Straße 25", 50.4353207328, 7.49241615241),
    ("Susvindsvägen 21", 57.1224, 12.28136),
    ("Sydhamnsgatan 12", 56.02898, 12.70587),
    ("Tallskogsvägen", 58.4925833, 13.13884665),
    ("Tradenvägen 6 (Håby gård)", 58.488548, 11.629203),
    ("Vallenvägen 5 (Stora Höga)", 58.023234, 11.840188),
    ("Vänersborgsvägen - Wallentinsvägen", 58.040512, 12.801716),
    ("Vasavägen 1", 57.78512, 14.23078),
    ("Veldkampsweg 26", 52.3522734, 6.656573),
    ("Vilangatan", 58.39008, 13.45906),
    ("Warodells väg 3", 58.150745, 13.55735775),
    ("Westfalenstraße  10", 51.32998815, 6.9783199233),
    ("Alte Heerstrasse 1 (Einum)", 52.161625, 10.007915),
    ("Düsseldorfer Landstraße 424 (Huckingen)", 51.35322, 6.743813),
    ("Grevesmühlener Straße  6", 53.829994, 11.2105979),
    ("Harburger Straße 18", 53.593769, 9.477032),
    ("Lornsenstraße 142", 53.610576, 9.840102),
    ("Mielestraße 20", 52.38042, 10.006417),
    ("Rolfinckstraße 48 (Wellingsbüttel)", 53.63925, 10.0894444444444),
    ("Segeberger Chaussee 345", 53.701913, 10.057361),
    ("Viktoriastraße 22 - 24", 52.288848, 8.937483),
    ("Wanderslebener Straße 24 (Mühlberg)", 50.873632, 10.830234),
    ("Nobelstraat 6", 52.363734, 5.652068),
    ("Nadorster Straße 253 (Nadorst)", 53.16482529, 8.22523532658),
    ("nan", 50.579804, 12.713364),
    ("Raiffeisenstraße 18", 53.4573333333333, 7.49766666666667),
    ("nan", 48.5438055555556, 10.3675555555556),
    ("Ängelholmsvägen 38", 56.06192, 12.71004),
    ("Skördevägen 2 (Lerberget)", 56.1808013916016, 12.5638999938965),
    ("Osterholzer Heerstraße 161 (Osterholz)", 53.0576111111111, 8.94875),
    ("Europaweg 1", 53.1672703156, 6.8662034432),
    ("Vossenkamp 8", 53.187931, 6.372576),
    ("nan", 53.31161, 7.45694),
    ("Berliner Straße 1-3 (Dorum)", 53.686583, 8.5718056),
    ("Celler Straße  58", 52.979862, 9.847354),
    ("Delmenhorster Straße 12", 52.90561, 8.442472),
    ("Hindenburgstraße 1", 53.374120512, 9.008448425),
    ("Industriestraße 2", 53.280638, 9.495867),
    ("Raiffeisenstraße 10 (Bad Bederkesa)", 53.629423, 8.816431),
    ("Stader Straße 40", 53.6811111111111, 9.17913888888889),
    ("Warsteiner Straße 41", 51.3604722222222, 8.28661111111111),
    ("Werderstraße 3-4", 53.46922, 12.02325),
    ("Wildeshauser Landstraße 60", 53.018135, 8.569942),
    ("Henleinstraße 1", 53.027897, 8.801319),
    ("['s-Hertogenbosch]", 51.685994, 5.281339),
    ("Anthony Fokkerweg 8", 52.344105, 4.842047),
    ("De Striptekenaar 83", 52.406789, 5.322229),
    ("Dijkje 20", 51.77126, 4.926719),
    ("Haardijk 3", 52.57459, 6.602568),
    ("Ookmeerweg 501", 52.354618, 4.769484),
    ("Parkweg 98", 52.220703, 6.870358),
    ("Randweg 18 ( )", 52.698176, 5.747978),
    ("Rondweg 3", 52.290259, 6.768244),
    ("Sögeler Straße 9", 52.84862082, 7.66563535),
    ("Chausseestraße 1", 52.31578, 13.6041389),
    ("Ruhlebener Straße 1a (Spandau)", 52.529141, 13.207393),
    ("Bahnhofstraße 2", 52.9684166666667, 7.34886111111111),
    ("Bassumer Straße 83", 52.687037, 8.783719),
    ("Emder Straße 33 (Georgsheil)", 53.47228, 7.31872),
    ("Gernröder Chaussee 1", 51.7716388888889, 11.1404166666667),
    ("Mindener Straße 2a", 52.20735, 8.801743),
    ("Monschauer Straße 69", 50.7932222222222, 6.47052777777778),
    ("Schönauer Straße 113 (Großzschocher)", 51.3106944444444, 12.3088333333333),
    ("Venloer Straße 1", 51.5201944444444, 6.31011111111111),
    ("Westersteder Straße 14a (Zetel)", 53.3864321, 7.95387878),
    (" Marconistraat 17", 52.497058, 6.126811),
    ("Kieler Straße 196 - 198 (Zentrum)", 54.0889444444444, 9.98669444444444),
    ("Cloppenburger Straße 224 (Kreyenbrück)", 53.117566, 8.214305),
    ("De Wissel 2", 53.268406, 5.659423),
    ("Dolderweg 48", 52.788152, 6.093207),
    ("Geraldadrift 2", 53.409509, 6.665944),
    ("Havenweg 23", 52.168234, 5.366542),
    ("Kissel 43", 50.890622, 5.99954),
    ("Okkenbroekstraat 19", 52.317137, 6.350114),
    ("Parkweg 85", 51.898633, 5.188285),
    ("Raalterweg 56", 52.332774, 6.205457),
    ("Sint Bonifaciuslaan 83", 51.424271, 5.506018),
    ("Stationsweg 24", 52.511044, 6.419701),
    ("Wijheseweg 45", 52.450177, 6.132063),
    ("Piet Van Donkplein 3", 52.24958383, 6.207222197),
    ("Schiedamsedijk 12", 51.908842, 4.365131),
    ("Seggelant-Zuid 1", 51.893914, 4.187602),
    ("nan", 52.497869, 9.456519),
    ("Cuxhavener Straße 31", 53.806573, 8.891136),
    ("Midslanderhoofdweg 5 (Midsland)", 53.381652, 5.289162),
    ("Uterwei 20", 53.223764, 6.175033),
    ("Lozerlaan 4 (De Uithof)", 52.040941, 4.244279),
    ("Rijksstraatweg 82", 52.51364188, 4.65287894),
    ("de Bolder 71", 53.117055, 6.073447),
    ("Jupiterweg 7", 53.196304, 5.844352),
    ("Transportweg 24", 52.160984, 4.785012),
    ("Bremer Straße 46", 52.8044, 8.647264),
    ("Hildesheimer Straße 407 (Wülfel)", 52.3264166666667, 9.78166666666667)
]

def get_osrm_route(waypoints):
    waypoint_str = ";".join(["{},{}".format(lon, lat) for lat, lon in waypoints])
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

def build_route_with_filtered_tankstations(start, end, tankstations, interval_km=250, corridor_km=100):
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
                if closest not in used_stations:
                    used_stations.append(closest)
                    waypoints.append((closest[1], closest[2]))
                else:
                    used_stations.append(("Geen OG tanklocatie mogelijk", curr_point[1], curr_point[0]))
                    waypoints.append((curr_point[1], curr_point[0]))
            else:
                used_stations.append(("Geen OG tanklocatie mogelijk", curr_point[1], curr_point[0]))
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


col1, col2 = st.columns([1, 8])
with col1:
    st.image("Alleen spark.png", width=50)
with col2:
    st.title("OG routekaart")

start_address = st.text_input("Startadres", value="")
end_address = st.text_input("Eindadres", value="")
route_name = st.text_input("Routenaam", value="Mijn Route")

interval_km = st.slider("Afstand tussen tankstops (km)", min_value=100, max_value=500, value=250, step=25)
corridor_km = st.slider("Maximale omweg vanaf hoofdlijn (km)", min_value=25, max_value=300, value=100, step=25)

if st.button("Genereer Route"):
    start = geocode_address(start_address)
    end = geocode_address(end_address)

    if not start or not end:
        st.error("Kon één van de adressen niet vinden.")
    else:
        waypoints, used_stations = build_route_with_filtered_tankstations(start, end, tankstations, interval_km=interval_km, corridor_km=corridor_km)
        route_coords = get_osrm_route([(wp[0], wp[1]) for wp in waypoints])
        if route_coords:
            df = pd.DataFrame(route_coords, columns=["Longitude", "Latitude"])
            df["Route"] = route_name
            st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

            st.subheader("📍 OG Tanklocaties op de route")
            tank_df = pd.DataFrame([
                {"Latitude": lat, "Longitude": lon, "Naam": name}
                for name, lat, lon in used_stations
            ])
            st.map(tank_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

            tank_df = tank_df.dropna(subset=["Latitude", "Longitude"])
            
            # Bereken totale routeafstand met tankstops
            totale_afstand = 0
            for i in range(1, len(route_coords)):
                p1 = route_coords[i - 1]
                p2 = route_coords[i]
                totale_afstand += geodesic((p1[1], p1[0]), (p2[1], p2[0])).km

            # Bereken afstand zonder tussenliggende tankstops
            originele_coords = get_osrm_route([start, end])
            originele_afstand = 0
            for i in range(1, len(originele_coords)):
                p1 = originele_coords[i - 1]
                p2 = originele_coords[i]
                originele_afstand += geodesic((p1[1], p1[0]), (p2[1], p2[0])).km

            st.write("🛣️ **Totale afstand met OG-tanklocaties:** {:.1f} km".format(totale_afstand))
            st.write("📏 **Afstand zonder tankstops:** {:.1f} km".format(originele_afstand))


            for i, (name, _, _) in enumerate(used_stations, 1):
                st.markdown("🛢️ **Tankmoment {}:** {}".format(i, name))
        else:
            st.error("Kon geen route genereren met OSRM.")