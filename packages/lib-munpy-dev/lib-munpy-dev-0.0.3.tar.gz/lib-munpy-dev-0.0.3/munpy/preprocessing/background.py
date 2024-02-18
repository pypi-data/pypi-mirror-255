import os

import numpy as np
import pandas as pd

import cdsapi
from datetime import datetime
import yaml
from netCDF4 import Dataset

from munpy.general import get_nc_index, dumpBinary, db_to_street_center
from munpy import config


def download_data(
    key_path, save_path,
    latitude, longitude,
    download_date=None, leadtime_hours=48
):
    """

    :param latitude:
    :param longitude:
    :param key_path:
    :param save_path:
    :param download_date: if None, aplica fecha de ejecución. Debe ser formato YYYY-MM-DD
    :param leadtime_hours:
    :return:
    """

    max_lat, min_lat = latitude + 0.5, latitude - 0.5
    max_lon, min_lon = longitude + 0.5, longitude - 0.5

    if not download_date:
        download_date = datetime.now().strftime('%Y-%m-%d')

    download_filename = os.path.join(save_path, 'copernicus_forecast.nc')

    # Load authentication credentials from the provided YAML file
    with open(key_path, 'r') as auth_file:
        credentials = yaml.safe_load(auth_file)

    c = cdsapi.Client(url=credentials['url'], key=credentials['key'])

    c.retrieve(
        'cams-europe-air-quality-forecasts',
        {
            'variable': [
                'ammonia', 'carbon_monoxide', 'formaldehyde', 'sulphur_dioxide',
                'nitrogen_dioxide', 'nitrogen_monoxide', 'ozone',
                'particulate_matter_10um', 'particulate_matter_2.5um',
            ],
            'model': 'ensemble',
            'level': '0',
            'date': f'{download_date}/{download_date}',
            'type': 'forecast',
            'time': '00:00',
            'leadtime_hour': [str(i) for i in range(leadtime_hours)],
            'area': [
                max_lat, min_lon,
                min_lat, max_lon,
            ],
            'format': 'netcdf',
        },
        download_filename
    )

    return download_filename


def set_variable_names(mode):
    """
    Define los nombres de las variables del archivo NC de background para los modos 'copernicus' y 'chimere'.
    :param mode: 'copernicus' o 'chimere'.
    :return: un diccionario 'gases' con los nombres de las variables.
    """

    if mode == 'copernicus':
        gases = {
            'co_conc': 'CO', 'nh3_conc': 'NH3', 'no2_conc': 'NO2',
            'no_conc': 'NO', 'o3_conc': 'O3', 'so2_conc': 'SO2',
            'pm10_conc': 'PM10', 'pm2p5_conc': 'PM25'
        }
    else:
        gases = {
            'CO': 'CO', 'NH3': 'NH3', 'NO2': 'NO2',
            'NO': 'NO', 'O3': 'O3', 'SO2': 'SO2',
            'PM10': 'PM10', 'PM25': 'PM25'
        }

    return gases


def process_background(city, key_path, date=None, mode='copernicus', leadtime_hours=48):
    """
    Dependiendo si el parámetro 'mode' es 'copernicus' o 'chimere', esta función hace dos cosas:
    descarga los datos de background de Copernicus y los procesa, o bien lee el archivo de
    salida de Chimere 'out.datehour_24_base.online.cpl4.nc' y lo procesa.

    :param city:
    :param key_path:
    :param date: Fecha en formato YYYY-MM-DD. Si es 'None', se aplica la fecha de hoy.
    :param mode: 'copernicus' para descargar los datos de copernicus y 'chimere' para leer arcivo generado por Chimere.
    :param leadtime_hours:
    :return:
    """

    city_dir = os.path.join(config.LEZ_DIR, city)
    street_file = os.path.join(city_dir, 'domain/street.csv')
    background_dir = os.path.join(city_dir, f'background/{date}')

    if not os.path.exists(background_dir):
        os.makedirs(background_dir)

    streets = pd.read_csv(street_file)
    streets = db_to_street_center(streets)
    N_streets = len(streets)
    mean_latitude, mean_longitude = streets[['center_lat', 'center_lon']].mean().values

    # Get NetCDF file
    if mode == 'copernicus':
        ncfile = download_data(key_path, background_dir, mean_latitude, mean_longitude, date, leadtime_hours)
    else:
        date_trimmed = date.replace('-', '')
        ncfile = os.path.join(background_dir, f'out.{date_trimmed}00_24_base.online.cpl4.nc')

    dataset = Dataset(ncfile, mode='r')

    # Set variable names
    gases = set_variable_names(mode)

    for gas in gases:
        gas_array = np.zeros((leadtime_hours, N_streets), dtype=np.float32)

        for i, st in streets.iterrows():
            center_lat, center_lon = st['center_lat'], st['center_lon']
            i_index, j_index, _ = get_nc_index(center_lat, center_lon, dataset, mode=mode)
            gas_street_values = dataset.variables[gas][:, 0, i_index, j_index]
            gas_array[:, i] = gas_street_values[:leadtime_hours]

        dumpBinary(gas_array, os.path.join(background_dir, f'{gases[gas]}.bin'))


if __name__ == "__main__":
    process_background('madrid', config.API_KEY, date='2023-11-22', mode='chimere', leadtime_hours=24)
