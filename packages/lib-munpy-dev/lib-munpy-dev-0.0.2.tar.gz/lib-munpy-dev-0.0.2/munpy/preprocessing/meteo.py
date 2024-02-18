import os.path
from datetime import datetime

import pandas as pd
import netCDF4

from munpy import config
from munpy.general import get_nc_index, db_to_street_center, dumpBinary
from munpy.preprocessing.meteo_functions import *


STREET_PARAMETERS = [
    'WindDirection', 'WindSpeed', 'PBLH', 'UST', 'LMO',
    'SpecificHumidity', 'SurfaceTemperature', 'LiquidWaterContent',
    'SolarRadiation', 'Rain', 'SurfacePressure'
]

INTER_PARAMETERS = [
    'WindDirection', 'WindSpeed',
    'PBLH', 'LMO', 'UST'
]


def get_param(parameter, latitude, longitude, ncdataset):
    """

    :param parameter: parameter to obtain
    :param latitude:
    :param longitude:
    :param ncdataset: WRF dataset
    :return:
    """

    i_index, j_index, _ = get_nc_index(latitude, longitude, ncdataset, mode='wrf')

    if parameter == 'WindSpeed':
        u_wind = ncdataset.variables[config.U_WIND][:, i_index, j_index]
        v_wind = ncdataset.variables[config.V_WIND][:, i_index, j_index]
        return_param, _ = process_wind(u_wind, v_wind)

    elif parameter == 'WindDirection':
        u_wind = ncdataset.variables[config.U_WIND][:, i_index, j_index]
        v_wind = ncdataset.variables[config.V_WIND][:, i_index, j_index]
        _, return_param = process_wind(u_wind, v_wind)

    elif parameter == 'PBLH':
        return_param = ncdataset.variables[config.PBLH][:, i_index, j_index]

    elif parameter == 'UST':
        return_param = ncdataset.variables[config.FRICTION_VELOCITY][:, i_index, j_index]

    elif parameter == 'LMO':
        friction_velocity = ncdataset.variables[config.FRICTION_VELOCITY][:, i_index, j_index]
        surface_pressure = ncdataset.variables[config.SURFACE_PRESSURE][:, i_index, j_index]
        surface_temperature = ncdataset.variables[config.SURFACE_TEMPERATURE][:, i_index, j_index]
        skin_temperature = ncdataset.variables[config.SKIN_TEMPERATURE][:, i_index, j_index]
        latent_heat = ncdataset.variables[config.LATENT_HEAT][:, i_index, j_index]
        sensible_heat = ncdataset.variables[config.SENSIBLE_HEAT][:, i_index, j_index]

        temperature_0 = skin_temperature * (surface_pressure / 101325.0) ** (-287.0 / 1005.0)
        mean_temperature = 0.5 * (temperature_0 + surface_temperature)
        evaporation = latent_heat / 2.5e9

        return_param = (
                - friction_velocity ** 3 * mean_temperature / (config.VON_KARMAN * config.G_ACCELL) /
                (sensible_heat + 0.608 * mean_temperature * evaporation)
        )

    elif parameter == 'SpecificHumidity':
        return_param = ncdataset.variables[config.SPECIFIC_HUMIDITY][:, 0, i_index, j_index]

    elif parameter == 'SurfaceTemperature':
        return_param = ncdataset.variables[config.SURFACE_TEMPERATURE][:, i_index, j_index]

    elif parameter == 'LiquidWaterContent':
        return_param = ncdataset.variables[config.CLOUD_MIXING_RATIO][:, 0, i_index, j_index]

    elif parameter == 'SolarRadiation':
        return_param = ncdataset.variables[config.SOLAR_RADIATION][:, i_index, j_index]

    elif parameter == 'Rain':
        convective_rain = ncdataset.variables[config.CONVECTIVE_RAIN][:, i_index, j_index]
        nonconvective_rain = ncdataset.variables[config.NON_CONVECTIVE_RAIN][:, i_index, j_index]
        total_rain = convective_rain + nonconvective_rain
        rain = np.zeros(total_rain.shape)
        rain[0] = total_rain[0]

        for i in range(1, rain.shape[0]):
            rain[i] = total_rain[i] - total_rain[i - 1]

        return_param = rain

    elif parameter == 'SurfacePressure':
        return_param = ncdataset.variables[config.SURFACE_PRESSURE][:, i_index, j_index]

    else:
        print(f'Wrong parameter name "{parameter}"')
        exit(1)

    return return_param


def process_meteo(domain, date_formatted=None, start_hour=None):
    """

    :param domain:
    :param date_formatted: yyyy-mm-dd
    :param start_hour: 00, 01, ..., 22, 23
    :return:
    """

    # Ajustar la hora
    if not start_hour:
        start_hour = '00'

    # Ajustar la fecha en función de si se ejecuta para un día anterior o para hoy.
    if not date_formatted:
        datetime_formatted = datetime.now().strftime('%Y-%m-%d') + f'_{start_hour}:00:00'
    else:
        datetime_formatted = date_formatted + f'_{start_hour}:00:00'

    # Definir todos los directorio y archivos necesarios
    domain_dir = os.path.join(config.LEZ_DIR, domain)
    raw_meteo_file = os.path.join(domain_dir, f'meteo/wrfout_d01_{datetime_formatted}')
    meteo_dir = os.path.join(domain_dir, f'meteo/{date_formatted}')
    street_file = os.path.join(domain_dir, 'domain/street.csv')
    inter_file = os.path.join(domain_dir, 'domain/intersection.csv')

    if not os.path.exists(meteo_dir):
        os.makedirs(meteo_dir)

    # Leer todos los archivos
    streets = pd.read_csv(street_file)
    streets = db_to_street_center(streets)
    intersections = pd.read_csv(inter_file)
    ncdataset = netCDF4.Dataset(raw_meteo_file)

    # Y extraer las dimensiones de las matrices
    N_streets, N_inters = len(streets), len(intersections)
    N_times = len(ncdataset.variables[config.TIMES][:])

    # Primero procesar los parámetros de las calles
    for street_param in STREET_PARAMETERS:
        param = np.zeros((N_times, N_streets))

        for i, st in streets.iterrows():
            street_lat, street_lon = st['center_lat'], st['center_lon']
            param[:, i] = get_param(street_param, street_lat, street_lon, ncdataset)
            filename = os.path.join(meteo_dir, f'{street_param}.bin')
            dumpBinary(param.astype(np.float32), filename)

    # Y por último procesar los parámetros de las intersecciones
    for inter_param in INTER_PARAMETERS:
        param = np.zeros((N_times, N_inters))

        for i, st in intersections.iterrows():
            street_lat, street_lon = st['lat'], st['lon']
            param[:, i] = get_param(inter_param, street_lat, street_lon, ncdataset)
            filename = os.path.join(meteo_dir, f'{inter_param}Inter.bin')
            dumpBinary(param.astype(np.float32), filename)


if __name__ == '__main__':
    process_meteo('madrid', date_formatted='2024-01-16', start_hour=21)
