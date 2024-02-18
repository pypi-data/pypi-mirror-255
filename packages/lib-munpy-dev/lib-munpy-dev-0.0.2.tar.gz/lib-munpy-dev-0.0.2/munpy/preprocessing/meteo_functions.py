import numpy as np


def process_wind(u_wind, v_wind):
    """
    :param u_wind: horizontal component of wind
    :param v_wind: vertical component of wind
    :return: wind_speed, wind_direction, velocity and direction of wind.
            phi = 0 for wind vector pointing notrh, phi = pi/2 for wind
            vector pointing south.
    """

    wind_speed = np.sqrt(u_wind ** 2 + v_wind ** 2)
    wind_direction = np.arctan2(u_wind, v_wind)  # Esta función devuelve el ángulo entre [-pi, pi)

    wind_direction = (wind_direction + 2*np.pi) % (2 * np.pi)  # remapear entre [0, 2*pi)

    return wind_speed, wind_direction


def compute_relative_humidity(specific_humidity, temperature, pressure):
    """
    Calcula la humedad relativa a partir de la humedad específica

    :param specific_humidity:
    :param temperature:
    :param pressure:
    :return:
    """
    p_sat = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))
    relative_humidity = specific_humidity * pressure / \
        ((0.62197 * (1.0 - specific_humidity) + specific_humidity) * p_sat)

    return relative_humidity


def compute_crh(surface_pressure, pressure):
    """
    Surface pressure -> 2D, Pressure -> 3D ==>
    :param surface_pressure:
    :param pressure:
    :return:
    """

    sig = np.zeros(pressure.shape)
    for i in range(pressure.shape[0]):
        sig[i, :] = pressure[i, :] / surface_pressure[i]

    crh = 1.0 - 2.0 * sig * (1.0 - sig) * (1.0 + (sig - 0.5) * np.sqrt(3))

    return crh


def compute_cloud_fraction(rh, crh):
    tmp = rh - crh
    cloud_fraction = tmp ** 2 / (1 - crh) ** 2
    negative_indices = np.where(
        np.logical_and(np.isclose(crh, 1), tmp < 0)
    )

    cloud_fraction[negative_indices] = 0.0

    return cloud_fraction


def compute_cloudiness_layer(pressure, bottom_thresshold, top_thresshold, cloud_fraction, gridz_inter):
    """
    Calcula la nubosidad en diferentes capas de la atmósfera dada una presión límite.

    :param pressure: presión atmosférica
    :param bottom_thresshold: límite inferior de presión
    :param top_thresshold: límite superior de presión
    :param cloud_fraction: fracción de nubosidad
    :param gridz_inter:
    :return:
    """

    # Calcular qué indices corresponden a las presiones que se encuentran entre los valores límite
    between_indices = np.where(
        np.logical_and(
            pressure > bottom_thresshold, pressure < top_thresshold
        )
    )

    # Como es posible que no todos los timestamps tengan el mismo número de valore entre top_thres y bottom_thres,
    # se ejecuta la siguiente parte del código de forma más manual. Se deben "integrar" los valores de nubosidad.
    cloudiness_time_series = np.zeros(cloud_fraction.shape[0])

    for time_stamp, height_level in zip(between_indices[0], between_indices[1]):
        cloudiness_time_series[time_stamp] += cloud_fraction[time_stamp, height_level] * (
            gridz_inter[time_stamp, height_level] - gridz_inter[time_stamp, height_level-1]
        )

    return cloudiness_time_series


def compute_attenuation(relative_humidity, medium_clouds, high_clouds, gridz):
    """

    :param relative_humidity:
    :param medium_clouds:
    :param high_clouds:
    :param gridz:
    :return:
    """

    # Dimensiones
    N_times, N_heights = relative_humidity.shape[0], relative_humidity.shape[1]

    # Coeficientes pochos
    a, b, c = 0.1, 0.3, 1.5

    attenuation = np.zeros(N_times)

    for i in range(N_times):
        att = 0.0
        norm_factor = 0.0

        for k in range(N_heights-1):
            if gridz[i, k] < 1500:
                dz = gridz[i, k+1] - gridz[i, k]
                norm_factor += 0.3 * dz

                if relative_humidity[i, k] > 0.7:
                    print(relative_humidity)
                    att += (relative_humidity[i, k] - 0.7) * dz

        att = att / norm_factor
        attenuation[i] = (1 - a * high_clouds[i]) * (1 - b * medium_clouds[i]) * np.exp(-c * att)

    return attenuation
