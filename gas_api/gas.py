import requests
from geopy import distance


def distancia(lat1, long1, lat2, long2):
    a = (lat1, long1)
    b = (lat2, long2)
    distancia_km = distance.distance(a, b).km
    return distancia_km


def carga_gasolineras():
    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    api_response = requests.get(url)
    data_dict = api_response.json()
    global estaciones_list
    estaciones_list = data_dict['ListaEESSPrecio']


def busca_gasolineras(user_lat, user_lon):
    msg_list = []
    for i in range(len(estaciones_list)):
        gaslat = float(estaciones_list[i]['Latitud'].replace(',', '.'))
        gaslon = float(estaciones_list[i]['Longitud (WGS84)'].replace(',', '.'))
        filtered = user_lat + 0.1 > gaslat > user_lat - 0.1 and user_lon + 0.1 > gaslon > user_lon - 0.1
        if filtered:
            distanciakm = distancia(user_lat, user_lon, gaslat, gaslon)
            rotulo = estaciones_list[i]["Rótulo"]
            diesel = estaciones_list[i]["Precio Gasoleo A"].replace(',', '.')
            gasolina95 = estaciones_list[i]["Precio Gasolina 95 E5"].replace(',', '.')
            distanciakm = "{:.2f}".format(distanciakm)
            msg = (f"⛽ <b>{rotulo}</b> \n"
                   f"- Diesel: {diesel}€ \n"
                   f"- Gasolina95: {gasolina95}€ \n"
                   f"📍 <a href='https://maps.google.com/maps?q={gaslat},{gaslon}'>Google Maps</a> {distanciakm} Km \n\n")
            msg_list.append(msg)
    msg_list.sort(key=lambda number: distanciakm)
    msg_list = msg_list[0:5]
    return msg_list
