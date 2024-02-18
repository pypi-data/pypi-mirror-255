import os.path
from datetime import datetime, timedelta
from typing import List
import pandas as pd

from munpy import config
from munpy.general import readBinary
from munpy.general import sql_connection


def bulk_load_simulation(
    simulation: pd.DataFrame, table, schema, db_url, db_name,
    db_user, db_password, db_port
):

    engine = sql_connection(db_url, db_name, db_user, db_password, port=db_port)
    simulation.to_sql(table, engine, schema=schema, if_exists='replace', index=False)


class Postprocessing:
    DATE_FORMAT = '%Y-%m-%d'
    TIMESTAMP_FORMAT = '%Y-%m-%d_%H:%M:%S'

    def __init__(self, city, simulation_date: datetime, save_start: datetime = None, save_end: datetime = None):
        """
        Todas las fechas deben ir en formato datetime.datetime.

        :param city:
        :param simulation_date: Fecha y hora a la que inicia la simulación de MUNICH
        :param save_start: Fecha y hora a partir de la que se quiere procesar la simulación
        :param save_end: Fecha y hora hasta la que se quiere procesar la simulación
        """
        self.city = city
        self.sim_start = simulation_date

        # Used in case not all hours of simulation are desired to be saved.
        self.save_start = save_start
        self.save_end = save_end

        self.N_hours = None
        self.N_ts_per_hours = None
        self.sim_end = None

        self._init_city()

    def process(self, delta_t: int) -> pd.DataFrame:
        """
        Postprocess MUNICH output data into a beautiful and easy to use DataFrame.

        :param delta_t: time separation between iterations in seconds.
        :return:
        """

        # Get time parameters from delta_t and a sample simulation output
        self._get_time_params(delta_t)

        # Get street_id index from domain data
        street_ids = self.street_df['street_id'].to_list()

        # Start processing gases
        results_dataframe = pd.DataFrame()
        results_dataframe = self._process_gases(results_dataframe)
        # results_dataframe = self._process_pms(results_dataframe)

        # Add street ids to results dataframe
        results_dataframe = self._add_street_index(results_dataframe, street_ids)
        results_dataframe = self._add_time_index(results_dataframe)

        # Finally, trim the dataframe to keep only the desired timestamps
        results_dataframe = self._trim_result_timestamps(results_dataframe)

        return results_dataframe

    def _trim_result_timestamps(self, results_dataframe: pd.DataFrame):
        desired_timestamps = pd.date_range(
            start=pd.to_datetime(self.save_start),
            end=pd.to_datetime(self.save_end),
            freq='H'
        )

        return results_dataframe.loc[desired_timestamps]

    def _add_street_index(self, results_dataframe: pd.DataFrame, street_ids: List[int]) -> pd.DataFrame:
        street_index = pd.Series([st_id for st_id in street_ids for _ in range(self.N_hours)])
        results_dataframe['street_id'] = street_index

        return results_dataframe

    def _add_time_index(self, results_dataframe: pd.DataFrame) -> pd.DataFrame:
        hourly_timestamps = pd.date_range(
            start=pd.to_datetime(self.sim_start),
            end=pd.to_datetime(self.sim_end),
            freq='H'
        )

        time_index = pd.Series([*hourly_timestamps] * self.N_streets)
        results_dataframe.set_index(time_index, inplace=True)

        return results_dataframe

    def _init_city(self) -> None:
        date_string = self.sim_start.strftime(Postprocessing.DATE_FORMAT)

        # Directories
        self.city_dir = os.path.join(config.LEZ_DIR, self.city)
        self.result_dir = os.path.join(self.city_dir, f'results/{date_string}')
        self.background_dir = os.path.join(self.city_dir, f'background/{date_string}')

        # Domain data
        street_file = os.path.join(self.city_dir, 'domain/street.dat')
        self.street_df = pd.read_csv(street_file, sep=';').rename(columns={'#id': 'street_id'})
        self.N_streets = len(self.street_df)

        # Check if there is anything to process
        self._check_results_exist()

    def _check_results_exist(self):
        if os.path.exists(self.result_dir) and len(os.listdir(self.result_dir)) > 0:
            return True

        return False

    def _get_time_params(self, delta_t: int) -> (int, int):
        sample_result_path = os.path.join(self.result_dir, 'NO2.bin')
        sample_result = readBinary(sample_result_path, N_streets=self.N_streets)
        N_timesteps = sample_result.shape[0]
        N_ts_per_hour = 3600 // delta_t
        N_sim_hours = N_timesteps // N_ts_per_hour

        self.N_hours = N_sim_hours
        self.N_ts_per_hour = N_ts_per_hour
        self.sim_end = self.sim_start + timedelta(hours=self.N_hours-1)

    def _process_gases(self, results_dataframe: pd.DataFrame) -> pd.DataFrame:
        for gas in [config.CO_COLUMN, config.NO2_COLUMN, config.NO_COLUMN, config.O3_COLUMN]:
            gas_result = self._get_gas_result(gas)
            gas_result = self._average_by_hours(gas_result)
            gas_result = self._ravel_result_to_series(gas_result)

            results_dataframe[gas] = gas_result

        return results_dataframe

    def _process_pms(self, results_dataframe: pd.DataFrame) -> pd.DataFrame:
        for pm in [config.PM10_COLUMN, config.PM25_COLUMN]:
            pm_result = self._get_pm_result(pm)
            pm_result = self._average_by_hours(pm_result)
            pm_result = self._ravel_result_to_series(pm_result)

            results_dataframe[pm] = pm_result

        return results_dataframe

    def _get_gas_result(self, gas):
        gas_file = os.path.join(self.result_dir, f'{gas.upper()}.bin')
        return readBinary(gas_file, N_streets=self.N_streets)

    def _get_pm_result(self, pm):
        pm_file = os.path.join(self.background_dir, f'{pm.upper()}.bin')
        return readBinary(pm_file, N_streets=self.N_streets)

    def _average_by_hours(self, gas_result):
        reshaped_result = gas_result.reshape((self.N_hours, self.N_ts_per_hour, self.N_streets))
        averaged_result = reshaped_result.mean(axis=1)

        return averaged_result

    def _ravel_result_to_series(self, gas_result):
        """
        Convierte un array de dimensiones (N_hoursteps, N_streets) a una Serie. "order = 'F'" ordena los valores de
        forma que aparecen seguidos todos los timesteps de la misma calle. Una vez pasados N_hour valores, empiezan
        los de la siguiente calle.
        :param gas_result:
        :return:
        """
        return pd.Series(gas_result.ravel(order='F'))


if __name__ == '__main__':
    sim_date = datetime.strptime('2024-01-09_21:00:00', Postprocessing.TIMESTAMP_FORMAT)
    start_save = datetime.strptime('2024-01-10_00:00:00', Postprocessing.TIMESTAMP_FORMAT)
    end_save = datetime.strptime('2024-01-10_23:00:00', Postprocessing.TIMESTAMP_FORMAT)

    valencia_postprocessing = Postprocessing('valencia', sim_date, start_save, end_save)
    results_2024_01_09 = valencia_postprocessing.process(delta_t=1200)
    print(results_2024_01_09)
