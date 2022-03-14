import requests
from geopy import distance


def distancia(lat1, long1, lat2, long2):
    punto_a = (lat1, long1)
    punto_b = (lat2, long2)
    distancia_km = distance.distance(punto_a, punto_b).km
    return distancia_km


def carga_gasolineras():
    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    api_response = requests.get(url)
    data_dict = api_response.json()
    global estaciones_list
    estaciones_list = data_dict['ListaEESSPrecio']


def busca_gasolineras(user_lat, user_lon):
    lista = []
    for i in range(len(estaciones_list)):
        gaslat = float(estaciones_list[i]['Latitud'].replace(',', '.'))
        gaslon = float(estaciones_list[i]['Longitud (WGS84)'].replace(',', '.'))
        pasar = gaslat > user_lat -0.15 and gaslat < user_lat + 0.15 and gaslon > user_lon -0.15 and gaslon < user_lon + 0.15        
        if pasar:
            distanciakm = distancia(user_lat, user_lon, gaslat, gaslon)
            rotulo = estaciones_list[i]["Rótulo"]
            diesel = estaciones_list[i]["Precio Gasoleo A"]
            gasolina95 = estaciones_list[i]["Precio Gasolina 95 E5"]
            gasolina98 = estaciones_list[i]["Precio Gasolina 98 E5"]
            if distanciakm < 3 and len(lista) < 5:
                msg = f"⛽ <b>{rotulo}</b> \n" \
                      f"- Diesel: {diesel}€ \n" \
                      f"- Gasolina95: {gasolina95}€ \n" \
                      f"📍 <a href='https://maps.google.com/maps?q={gaslat},{gaslon}'>Google Maps</a> {round(distanciakm, 2)} Km \n\n\n"
                lista.append(msg)
    return lista
