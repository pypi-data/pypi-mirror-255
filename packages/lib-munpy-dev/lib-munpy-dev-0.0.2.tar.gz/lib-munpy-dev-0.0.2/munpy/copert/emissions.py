import numpy as np
import pandas as pd

from munpy import config
from munpy.copert import copert


def import_link_data(df):
    """
    Import link data from the given DataFrame and configuration variables.

    Args:
        df (pd.DataFrame): DataFrame containing link data.

    Returns:
        Tuple: A tuple containing data_id, data_flow, data_distance, and speed.
    """
    data_id = np.array(df['street_id'])
    data_flow = np.array(df['volume'])
    data_distance = np.array(df['length'])
    speed = config.SPEED

    return data_id, data_flow, data_distance, speed


def import_vehicle_fleet_data():
    """
    Import vehicle fleet data.

    Returns:
        Tuple: A tuple containing engine_capacity_gasoline, engine_capacity_diesel, gasoline_proportion,
        and passenger_car_proportion.
    """
    engine_capacity_gasoline = np.array(
        [config.ENGINE_CAPACITY_GASOLINE_LESS_1P4, config.ENGINE_CAPACITY_GASOLINE_1P4_TO_2P0,
         config.ENGINE_CAPACITY_GASOLINE_MORE_2])
    engine_capacity_diesel = np.array(
        [config.ENGINE_CAPACITY_DIESEL_LESS_1P4, config.ENGINE_CAPACITY_DIESEL_1P4_TO_2P0,
         config.ENGINE_CAPACITY_DIESEL_MORE_2])
    gasoline_proportion = config.GASOLINE_PROPORTION
    passenger_car_proportion = config.PASSENGER_PROPORTION

    return engine_capacity_gasoline, engine_capacity_diesel, gasoline_proportion, passenger_car_proportion


def compute_emissions(cop, wanted_copert_classes, wanted_pollutants,
                      n_links, data_flow, data_distance, speed,
                      engine_capacities, engine_capacity_gasoline, engine_capacity_diesel, engine_types,
                      gasoline_proportion, passenger_car_proportion):
    """
    Computes the hot emissions (in g) for passenger cars at link resolution.

    Args:
        cop (Copert): An instance of the Copert class.
        wanted_copert_classes (list): List of wanted Copert classes.
        wanted_pollutants (list): List of wanted pollutants.
        n_links (int): Number of links.
        data_flow (numpy.ndarray): Array containing flow data.
        data_distance (numpy.ndarray): Array containing distance data.
        speed (float): Average travel speed.
        engine_capacities (list): List of engine capacities.
        engine_capacity_gasoline (numpy.ndarray): Gasoline engine capacity data.
        engine_capacity_diesel (numpy.ndarray): Diesel engine capacity data.
        engine_types (list): List of engine types.
        gasoline_proportion (float): Proportion of gasoline vehicles.
        passenger_car_proportion (float): Proportion of passenger cars.

    Returns:
        numpy.ndarray: Computed emissions data.
    """
    # Ranges for loops
    n_wanted_pollutants = len(wanted_pollutants)
    n_timesteps = config.N_TIMESTEPS
    n_engine_types = len(engine_types)
    n_wanted_classes = len(wanted_copert_classes)
    n_engine_capacities = len(engine_capacities)

    # Engine type and capacity distributions
    engine_type_distribution = [gasoline_proportion,
                                1. - gasoline_proportion]
    engine_capacity_distribution = [engine_capacity_gasoline,
                                    engine_capacity_diesel]
    # Some fixed parameters
    vehicle_type = cop.vehicle_type_passenger_car
    ambient_temperature = 20.

    computed_emissions = np.zeros(shape=(n_wanted_pollutants, n_links, config.N_TIMESTEPS), dtype=float)
    for p_ind in range(n_wanted_pollutants):  # pollutant index (from 0 to n_wanted_pollutants - 1)
        pollutant = wanted_pollutants[p_ind]  # pollutant integer value
        for i in range(n_links):
            flow = data_flow[i]
            distance = data_distance[i]
            for ts in range(n_timesteps):
                hot_emission = 0
                for t_ind in range(n_engine_types):
                    engine_type_distr = engine_type_distribution[t_ind]
                    engine_type = engine_types[t_ind]
                    for c_ind in range(n_wanted_classes):  # copert_params class index (from 0 to n_wanted_classes - 1)
                        copert_class = wanted_copert_classes[c_ind]  # copert_class integer value
                        for k_ind in range(n_engine_capacities):
                            engine_capacity_distr = engine_capacity_distribution[t_ind][k_ind]
                            engine_capacity = engine_capacities[k_ind]
                            if (copert_class != cop.class_Improved_Conventional
                                and copert_class != cop.class_Open_loop) \
                                    or engine_capacity <= 2.0:
                                # No formula available for diesel passenger cars whose
                                # engine capacity is less than 1.4 l and the copert_params class
                                # is Euro 1, Euro 2 or Euro 3.
                                if t_ind == 1 and k_ind == 0 \
                                        and copert_class in range(cop.class_Euro_1, 1 + cop.class_Euro_3):
                                    continue
                                e = cop.Emission(pollutant, speed, distance, vehicle_type, engine_type,
                                                 copert_class, engine_capacity, ambient_temperature)
                                e *= engine_type_distr * engine_capacity_distr
                                hot_emission += e * passenger_car_proportion
                    computed_emissions[p_ind][i][ts] = hot_emission * flow  # todo: restablecer?
    return computed_emissions


def emission_matrix_algorithm(
    pollutant, traffic_matrix, street_df,
    cop, temperature, wanted_copert_classes,
    speed, engine_capacities, engine_capacity_gasoline,
    engine_capacity_diesel, engine_types, gasoline_proportion,
    passenger_car_proportion
):
    # Ranges for loops
    n_engine_capacities = len(engine_capacities)

    # Engine type and capacity distributions
    engine_type_distribution = [gasoline_proportion,
                                1. - gasoline_proportion]
    engine_capacity_distribution = [engine_capacity_gasoline,
                                    engine_capacity_diesel]
    # Some fixed parameters
    vehicle_type = cop.vehicle_type_passenger_car

    N_times, N_streets = traffic_matrix.shape
    emitted_pollutant = np.zeros(traffic_matrix.shape)

    for street in range(N_streets):
        distance = street_df['length'].iloc[street]

        for timestep in range(N_times):
            hot_emission = 0

            for t_ind, (engine_type, engine_type_distr) in enumerate(zip(engine_types, engine_type_distribution)):

                for c_ind, copert_class in enumerate(wanted_copert_classes):

                    for k_ind in range(n_engine_capacities):
                        engine_capacity_distr = engine_capacity_distribution[t_ind][k_ind]
                        engine_capacity = engine_capacities[k_ind]
                        if (copert_class != cop.class_Improved_Conventional
                            and copert_class != cop.class_Open_loop) \
                                or engine_capacity <= 2.0:
                            # No formula available for diesel passenger cars whose
                            # engine capacity is less than 1.4 l and the copert_params class
                            # is Euro 1, Euro 2 or Euro 3.
                            if t_ind == 1 and k_ind == 0 \
                                    and copert_class in range(cop.class_Euro_1, 1 + cop.class_Euro_3):
                                continue
                            e = cop.Emission(pollutant, speed, distance, vehicle_type, engine_type,
                                             copert_class, engine_capacity, temperature)
                            e *= engine_type_distr * engine_capacity_distr
                            hot_emission += e * passenger_car_proportion

            emitted_pollutant[timestep, street] = hot_emission * traffic_matrix[timestep, street]

    return emitted_pollutant


def calculate_emission_matrix(
    traffic_matrix: np.ndarray, street_df: pd.DataFrame,
    pollutant, average_speed, temperature
):
    # Copert Class instance
    cop = copert.Copert(config.PC_FILE, config.LDV_FILE, config.HDV_FILE, config.MOTO_FILE)

    # Fleet vehicle data
    engine_capacity_gas, engine_capacity_dies, gasoline_prop, passenger_car_prop = import_vehicle_fleet_data()

    # Engine capacities and types
    engine_cap = [copert.Copert.engine_capacity_0p8_to_1p4,
                  copert.Copert.engine_capacity_1p4_to_2]
    engine_tps = [copert.Copert.engine_type_gasoline, copert.Copert.engine_type_diesel]

    # Standards that want to be computed
    wanted_copert_clss = [cop.class_Euro_1, cop.class_Euro_2, cop.class_Euro_3,
                          cop.class_Euro_4, cop.class_Euro_5, cop.class_Euro_6,
                          cop.class_Euro_6c]

    return emission_matrix_algorithm(
        pollutant, traffic_matrix, street_df, cop, temperature,
        wanted_copert_clss, average_speed, engine_cap, engine_capacity_gas,
        engine_capacity_dies, engine_tps, gasoline_prop, passenger_car_prop
    )


def generate_output_dataframe(name_pollutant, wanted_pollutants, computed_emissions, data_id):
    """
    Generate an output dataframe containing emissions data.

    Args:
        name_pollutant (list): List of all pollutants names.
        wanted_pollutants (list): List of wanted pollutants.
        computed_emissions (numpy.ndarray): Computed emissions data.
        data_id (numpy.ndarray): Array containing street IDs.

    Returns:
        Output dataframe with emissions data.
    """
    df = pd.DataFrame()
    df['street_id'] = data_id

    n_wanted_pollutants = len(wanted_pollutants)
    for p_ind in range(n_wanted_pollutants):  # pollutant index (from 0 to n_wanted_pollutants - 1)
        pollutant = wanted_pollutants[p_ind]  # pollutant integer value
        name = name_pollutant[pollutant]  # pollutant name
        if name == "NOx":
            column_name1 = "no2"
            column_name2 = "no"
            df[column_name2] = computed_emissions[p_ind][:, 0] * config.NO2_PROPORTION
            df[column_name1] = computed_emissions[p_ind][:, 0] * config.NO_PROPORTION
        elif name == "PM":
            column_name1 = "pm10"
            column_name2 = "pm25"
            df[column_name2] = computed_emissions[p_ind][:, 0] * config.PM10_PROPORTION
            df[column_name1] = computed_emissions[p_ind][:, 0] * config.PM25_PROPORTION
        else:
            if name == "HC":
                column_name = "ch4"
            else:
                column_name = name.lower()
            df[column_name] = computed_emissions[p_ind][:, 0]

    return df


def generate_output_dataframes(name_pollutant, wanted_pollutants, computed_emissions, data_id):
    """
    Generate separate DataFrames for each pollutant's emissions data.

    Args:
        name_pollutant (list): List of all pollutants names.
        wanted_pollutants (list): List of wanted pollutants.
        computed_emissions (numpy.ndarray): Computed emissions data.
        data_id (numpy.ndarray): Array containing street IDs.

    Returns:
        Dictionary of DataFrames where keys are pollutant names.
    """
    output_dataframes = {}

    n_wanted_pollutants = len(wanted_pollutants)
    for p_ind in range(n_wanted_pollutants):
        pollutant = wanted_pollutants[p_ind]
        name = name_pollutant[pollutant]

        if name == "NOx":
            df1 = pd.DataFrame(computed_emissions[p_ind],
                               columns=[f"t{t}" for t in range(config.N_TIMESTEPS)]) * config.NO2_PROPORTION
            df2 = pd.DataFrame(computed_emissions[p_ind],
                               columns=[f"t{t}" for t in range(config.N_TIMESTEPS)]) * config.NO_PROPORTION
            df1.insert(0, 'street_id', data_id)
            df2.insert(0, 'street_id', data_id)

            output_dataframes['no2'] = df1
            output_dataframes['no'] = df2
        elif name == "PM":
            df1 = pd.DataFrame(computed_emissions[p_ind],
                               columns=[f"t{t}" for t in range(config.N_TIMESTEPS)]) * config.PM10_PROPORTION
            df2 = pd.DataFrame(computed_emissions[p_ind],
                               columns=[f"t{t}" for t in range(config.N_TIMESTEPS)]) * config.PM25_PROPORTION
            df1.insert(0, 'street_id', data_id)
            df2.insert(0, 'street_id', data_id)

            output_dataframes['pm10'] = df1
            output_dataframes['pm25'] = df2
        else:
            df = pd.DataFrame(computed_emissions[p_ind], columns=[f"t{t}" for t in range(config.N_TIMESTEPS)])
            df.insert(0, 'street_id', data_id)

            if name == "HC":
                output_dataframes['ch4'] = df
            else:
                output_dataframes[name.lower()] = df

    return output_dataframes


def calculate_traffic_emissions(traffic_df):
    """
    Calculate emissions based on traffic data and vehicle fleet information using the Copert library.

    Args:
        traffic_df (pd.DataFrame): A DataFrame containing traffic data. It should include columns
        for street identifiers ('id'), traffic volume ('volume'), and street length ('length').

    Returns:
        pd.DataFrame: A pandas DataFrame with calculated emissions for various pollutants and streets.
        Columns include 'street_id' (street identifier) and columns for different pollutants such as
        CO, HC, NOx, and PM, with emissions estimated based on the provided traffic data and vehicle fleet information.
    """
    # Create an instance of the Copert class with the provided configuration file paths.
    cop = copert.Copert(config.PC_FILE, config.LDV_FILE, config.HDV_FILE, config.MOTO_FILE)

    # Load link data
    data_street_id, data_volume, data_length, avg_speed = import_link_data(traffic_df)
    n_streets = len(traffic_df)

    # Load vehicle fleet data
    engine_capacity_gas, engine_capacity_dies, gasoline_prop, passenger_car_prop = import_vehicle_fleet_data()
    engine_cap = [cop.engine_capacity_0p8_to_1p4,
                  cop.engine_capacity_1p4_to_2]
    engine_tps = [cop.engine_type_gasoline, cop.engine_type_diesel]

    # Standards that are going to be used to compute emissions
    # (No formula available for HC, PM, FC for emission standard of pre-Euro).
    wanted_copert_clss = [cop.class_Euro_1, cop.class_Euro_2, cop.class_Euro_3,
                          cop.class_Euro_4, cop.class_Euro_5, cop.class_Euro_6,
                          cop.class_Euro_6c]

    # Pollutants for which emissions are going to be computed (When including FC and VOC ---> IndexError: index 4 is
    # out of bounds for axis 0 with size 4)
    wanted_polltnts = [cop.pollutant_CO, cop.pollutant_HC, cop.pollutant_NOx, cop.pollutant_PM]

    # Names of the pollutants that can be computed by 'Copert' class
    name_polltnt = cop.name_pollutant

    # Compute emissions
    emissions = compute_emissions(cop, wanted_copert_clss, wanted_polltnts,
                                  n_streets, data_volume, data_length, avg_speed,
                                  engine_cap, engine_capacity_gas, engine_capacity_dies, engine_tps,
                                  gasoline_prop, passenger_car_prop)

    # Generate output dataframe
    emissions_dataframe = generate_output_dataframe(name_polltnt, wanted_polltnts, emissions, data_street_id)

    # # Generate output dataframes
    # emisions_dataframes = generate_output_dataframes(name_polltnt, wanted_polltnts, emissions, data_street_id)

    return emissions_dataframe


if __name__ == "__main__":
    # # Emission dataframe test
    # base_traffic = pd.read_csv('/home/ngomariz/LEZ-cities/lindau/base_traffic.csv')
    # emissions_df = calculate_traffic_emissions(base_traffic)

    # Emission matrix test
    traffic = np.random.randint(0, 100, size=(20, 100))
    streets = pd.read_csv('/home/ngomariz/LEZ-cities/test/domain/street.dat', sep=';')
    no2_emission = calculate_emission_matrix(
        traffic, streets, copert.Copert.pollutant_NOx,
        average_speed=40.0, temperature=20.0
    )
