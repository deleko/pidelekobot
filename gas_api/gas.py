import requests
from geopy import distance


def geodistance(lat1, long1, lat2, long2):
    a = (lat1, long1)
    b = (lat2, long2)
    km = distance.distance(a, b).km
    return km


def gas_load():
    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    api_response = requests.get(url)
    data_dict = api_response.json()
    global gas_list
    gas_list = data_dict['ListaEESSPrecio']


def gas_search(user_lat, user_lon):
    gas_found = []
    for i in range(len(gas_list)):
        gaslat = float(gas_list[i]['Latitud'].replace(',', '.'))
        gaslon = float(gas_list[i]['Longitud (WGS84)'].replace(',', '.'))
        filtered = user_lat + 0.1 > gaslat > user_lat - 0.1 and user_lon + 0.1 > gaslon > user_lon - 0.1
        if filtered:
            km_distancie = round(geodistance(user_lat, user_lon, gaslat, gaslon), 2)
            title = gas_list[i]["Rótulo"]
            diesel_price = gas_list[i]["Precio Gasoleo A"].replace(',', '.')
            gasolina95_price = gas_list[i]["Precio Gasolina 95 E5"].replace(',', '.')
            gas = {
                "title": title,
                "lat": gaslat,
                "lon": gaslon,
                "km_distancie": km_distancie,
                "diesel_price": diesel_price,
                "gasolina95_price": gasolina95_price
            }
            gas_found.append(gas)
    gas_found = sorted(gas_found, key=lambda x: x['km_distancie'])
    gas_found = gas_found[0:5]

    msg_list = [f"⛽ <b>{gas['title']}</b> \n"
                f"- Diesel: {gas['diesel_price']}€ \n"
                f"- Gasolina95: {gas['gasolina95_price']}€ \n"
                f"📍 <a href='https://maps.google.com/maps?q={gas['lat']},{gas['lon']}'>Google Maps</a> {gas['km_distancie']} Km \n\n"
                for gas in gas_found]

    return msg_list
