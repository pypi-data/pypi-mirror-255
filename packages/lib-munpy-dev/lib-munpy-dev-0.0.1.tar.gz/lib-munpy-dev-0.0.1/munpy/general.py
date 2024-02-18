import os
import json
from typing import List

import numpy as np
import pandas as pd

import psycopg
from sqlalchemy import create_engine

from munpy import config


def readBinary(filename: str, N_streets: int, dtype=np.float32, mode='array'):
    """
    Los outputs/inputs del modelo tienen la distribución (Nt, N_st)
    es decir pasos temporales X número de calles. Los binarios se cargan
    en un array de numpy justo con este formato. Si se desea se devuelven
    como dataframe.

    :param filename: archivo binario para decodificar.
    :param N_streets: número de calles de la simulación.
    :param dtype: tipo de dato guardado.
    :param mode: devolver como np.ndarray o como pd.DataFrame.
    :return: numpy.ndarray | pd.DataFrame
    """
    byte_size = np.dtype(dtype).itemsize
    Nt = int(
        os.stat(filename)[6] / byte_size / N_streets
    )
    length = Nt * N_streets
    data = np.fromfile(filename, dtype, length)
    data.shape = (Nt, N_streets)

    if mode == 'df':
        data = pd.DataFrame(data)

    return data


def dumpBinary(array: np.ndarray, filename: str):
    array.tofile(filename)


def dat_to_db(streets: pd.DataFrame, intersections: pd.DataFrame):
    """
    Converts the content of streets to format of crate database.

    :param streets: DataFrame loaded from 'street.dat'
    :param intersections: DataFrame lodaded from the raw intersections
    file, that only contains an intersectoin id and its coordinates.

    :return: DataFrame with street_id and a LineString of its coordinates.
    """

    ids, coordinates = [], []
    for _, street in streets.iterrows():
        ids.append(int(street['street_id']))
        first_inter = int(street['begin_inter'])
        second_inter = int(street['end_inter'])

        coords_ini = intersections.loc[
            intersections['node_id'] == first_inter, ['lon', 'lat']
        ].to_numpy()[0]

        coords_fin = intersections.loc[
            intersections['node_id'] == second_inter, ['lon', 'lat']
        ].to_numpy()[0]

        coordinates.append([list(coords_ini), list(coords_fin)])

    return pd.DataFrame({'street_id': ids, 'coordinates': coordinates})


def dat_to_street_center(streets: pd.DataFrame, intersections: pd.DataFrame):
    """
    Genera e archivo all_streets.csv, que contiene street_id y centro de las coordenadas
    :param streets: load(street.dat)
    :param intersections: load(raw_intersection.dat))
    :return:
    """

    street_dataframe = dat_to_db(streets, intersections)
    center_lat = [
        np.mean(coords, axis=0)[1]
        for coords in street_dataframe['coordinates']
    ]
    center_lon = [
        np.mean(coords, axis=0)[0]
        for coords in street_dataframe['coordinates']
    ]

    street_dataframe['lat'] = center_lat
    street_dataframe['lon'] = center_lon

    return street_dataframe


def db_to_street_center(streets: pd.DataFrame):
    """
    Añade una columna con el centro de la calle al csv de calles. Exactamente igual que
    dat_to_street_center pero empezando desde el formato database.
    :param streets:
    :return:
    """

    center_lat = [
        np.mean(json.loads(coords), axis=0)[1]
        for coords in streets['coordinates']
    ]
    center_lon = [
        np.mean(json.loads(coords), axis=0)[0]
        for coords in streets['coordinates']
    ]

    streets['center_lat'] = center_lat
    streets['center_lon'] = center_lon

    return streets


def dat_to_geojson(streets: pd.DataFrame, intersections: pd.DataFrame, color=None):
    """
    Genera un geojson de calles a partir del dataframe.
    :param streets:
    :param intersections:
    :param color: color con el que pintar las calles, ej: #ff0000 rojo puro
    :return:
    """

    streets = dat_to_db(streets, intersections)

    features = []
    for _, street in streets.iterrows():
        # GeoJSON lee por defecto las coordenadas en [longitud, latitud]
        coords = street['coordinates']

        feature = {
            "type": "Feature",
            "properties": {
                "id": str(street['street_id'])
            },
            "geometry": {
                "coordinates": coords,
                "type": "LineString"
            }
        }

        if color:
            feature['properties']["stroke"] = color

        features.append(feature)

    geojs = {"type": "FeatureCollection", "features": features}

    return geojs


def is_in_list(pair: List, existing_pairs: List) -> bool:
    """ Comprueba si ya existe determinada calle

    Args:
        pair (List): nueva calle
        existing_pairs (List): calles añadidas anteriormente

    Returns:
        bool: True/False si la calle está o no está en la lista.
    """

    pair_rev = pair.copy()
    pair_rev.reverse()

    return (pair in existing_pairs) or (pair_rev in existing_pairs)


def findStreets(intersection_id: int, streets: pd.DataFrame) -> List:
    """ Encuentra qué calles forman la intersección con id "intersection_id".

    Args:
        intersection_id (int): intersección de interés
        streets (pd.DataFrame): dataframe generado con el script "streets.py"

    Returns:
        List: lista con los ids de las calles que forman la intersección.
    """

    streets_as_array = streets[["begin_inter", "end_inter"]].to_numpy()

    # Encontrar todas las calles en las que aparece "intersection_id"
    positions = np.where(np.any(intersection_id == streets_as_array, axis=1))[0]
    streets_with_intersection = streets.loc[positions]
    street_ids = streets_with_intersection["street_id"].to_numpy().ravel()
    return list(street_ids)


def haversine_distance(coords_1, coords_2, r=6371.0, mode='grad'):
    """
    Calcula la distancia entre 2 puntos con coordenadas (lon_i, lat_i) expresada
    en grados.

    :param coords_1:
    :param coords_2:
    :param r:
    :param mode: 'grad' --> las coordenadas están expresadas en grados.
    'rad' --> las coordenadas están expresadas en radianes
    :return: distancia en metros
    """

    """
    coords_shape = coords_1.shape
    if len(coords_shape) == 2:
        lat1, lon1 = coords_1[:, 0], coords_1[:, 1]
        lat2, lon2 = coords_2[:, 0], coords_2[:, 1]
    else:
        lat1, lon1 = coords_1
        lat2, lon2 = coords_2
    """

    lon1, lat1 = coords_1
    lon2, lat2 = coords_2

    # Convert latitudes and longitudes to radians
    if mode == 'grad':
        lat1 = lat1 * np.pi/180
        lon1 = lon1 * np.pi/180
        lat2 = lat2 * np.pi/180
        lon2 = lon2 * np.pi/180

    # Calculate differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Apply haversine formula
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # Calculate distance
    distance = r * c
    return distance * 1000


def get_nc_index(lez_latitude, lez_longitude, ncdataset, mode='chimere'):
    """
    Obtiene el índice de interés del Dataset NETCDF a partir de una latitud
    y una longitud.

    :param lez_latitude:
    :param lez_longitude:
    :param ncdataset:
    :param mode: ['chimere', 'copernicus']. Si se usa en modo 'chimere', los nombres
    de latitud y longitud son 'XLAT', 'XLONG'. No obstante, en modo 'copernicus', los
    nombres son 'latitude' y 'longitude'.
    :return:
    """

    if mode == 'wrf':
        lat_name, lon_name = config.LATITUDE, config.LONGITUDE
        nc_latitude, nc_longitude = (ncdataset.variables[lat_name][0, :, :],
                                     ncdataset.variables[lon_name][0, :, :])

        N_lats, N_lons = nc_latitude.shape[-2:]
        i_min_distance = j_min_distance = 0
        min_distance = haversine_distance(
            [lez_latitude, lez_longitude],
            [nc_latitude[0, 0], nc_longitude[0, 0]]
        )

        for i in range(N_lats):
            for j in range(N_lons):
                dist = haversine_distance(
                    [lez_latitude, lez_longitude],
                    [nc_latitude[i, j], nc_longitude[i, j]]
                )

                if dist < min_distance:
                    min_distance = dist
                    i_min_distance = i
                    j_min_distance = j

    elif mode == 'chimere':
        lat_name, lon_name = 'lat', 'lon'
        nc_latitude, nc_longitude = (ncdataset.variables[lat_name][:, :],
                                     ncdataset.variables[lon_name][:, :])

        N_lats, N_lons = nc_latitude.shape[-2:]
        i_min_distance = j_min_distance = 0
        min_distance = haversine_distance(
            [lez_latitude, lez_longitude],
            [nc_latitude[0, 0], nc_longitude[0, 0]]
        )

        for i in range(N_lats):
            for j in range(N_lons):
                dist = haversine_distance(
                    [lez_latitude, lez_longitude],
                    [nc_latitude[i, j], nc_longitude[i, j]]
                )

                if dist < min_distance:
                    min_distance = dist
                    i_min_distance = i
                    j_min_distance = j

    else:
        lat_name, lon_name = 'latitude', 'longitude'
        nc_latitude, nc_longitude = (ncdataset.variables[lat_name][:],
                                     ncdataset.variables[lon_name][:])

        N_lats, N_lons = len(nc_latitude), len(nc_longitude)
        i_min_distance = j_min_distance = 0
        min_distance = haversine_distance(
            [lez_latitude, lez_longitude],
            [nc_latitude[0], nc_longitude[0]]
        )

        for i in range(N_lats):
            for j in range(N_lons):
                dist = haversine_distance(
                    [lez_latitude, lez_longitude],
                    [nc_latitude[i], nc_longitude[i]]
                )

                if dist < min_distance:
                    min_distance = dist
                    i_min_distance = i
                    j_min_distance = j

    # WARNINGS
    if not np.min(nc_latitude) < lez_latitude < np.max(nc_latitude):
        print(f'WARGING: LEZ latitude out of WRF simulation domain:')
        print(f'{np.min(nc_latitude)} ?< {lez_latitude} ?< {np.max(nc_latitude)}')

    if not np.min(nc_longitude) < lez_longitude < np.max(nc_longitude):
        print(f'WARGING: LEZ longitude out of WRF simulation domain:')
        print(f'{np.min(nc_longitude)} ?< {lez_longitude} ?< {np.max(nc_longitude)}')

    if min_distance >= 2e4:
        print(f'WARNING: Retrieving meteorological data from too far ({min_distance / 1000} km)')

    return i_min_distance, j_min_distance, min_distance


def sql_connection(host, database, user, password, port):
    """

    :param host:
    :param database:
    :param user:
    :param password:
    :param port:
    :return:
    """

    db_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(db_url)
    return engine


def connect(url, db, user, password, port):
    params_dic = {
        "host": url,
        "dbname": db,
        "user": user,
        "password": password,
        "port": port,
    }

    try:
        # connect to the PostgreSQL server
        conn = psycopg.connect(**params_dic)
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
        exit(1)
    return conn


def dataframe_to_postgresql(conn, insert_query):
    cursor = conn.cursor()
    try:
        cursor.execute(insert_query)
        conn.commit()
    except (Exception, psycopg.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    cursor.close()


def postgresql_to_dataframe(conn, select_query):
    """
    Function to download a dataframe from a query

    :param conn: the connection object (connect method)
    :param select_query: the query
    :type select_query: str
    :return: DataFrame obtained from the query
    :rtype: pandas.DataFrame
    """

    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return None

    # Naturally we get a list of tuples
    tuples = cursor.fetchall()

    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tuples, columns=[e.name for e in cursor.description])
    cursor.close()

    return df


if __name__ == '__main__':
    valencia = 'valencia'
    city_dir = os.path.join(config.LEZ_DIR, valencia)
    domain_dir = os.path.join(city_dir, 'domain')

    street_df = pd.read_csv(os.path.join(domain_dir, 'street.csv'))
    intersecton_df = pd.read_csv(os.path.join(domain_dir, 'intersection.csv'))

    gjs = dat_to_geojson(street_df, intersecton_df)
