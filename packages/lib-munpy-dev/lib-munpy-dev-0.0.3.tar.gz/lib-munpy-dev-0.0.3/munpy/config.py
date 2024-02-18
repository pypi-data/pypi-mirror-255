import os

############
# FILE PATHS
############
LEZ_DIR = os.getenv('LEZ_DIR', '/home/ngomariz/LEZ-cities')
WRF_DIR = os.getenv('WRF_DIR')
API_KEY = os.getenv('API_KEY')

##############
# Data sources
##############
OSM_API = os.getenv('OSM_API', '4.236.182.90')

############
# CONSTANTES
############
VON_KARMAN = 0.41
G_ACCELL = 9.81
R = 287.0

###################
# REGULAR VARIABLES
###################
TIMES = os.getenv('TIMES', 'Times')
LATITUDE = os.getenv('LATITUDE', 'XLAT')
LONGITUDE = os.getenv('LONGITUDE', 'XLONG')

######################################
# LIST OF WRF METEOROLOGICAL VARIABLES
######################################
U_WIND = os.getenv('U_WIND', 'U10')  # 3D
V_WIND = os.getenv('V_WIND', 'V10')  # 3D
PBLH = os.getenv('PHBL', 'PBLH')  # 3D
FRICTION_VELOCITY = os.getenv('UST', 'UST')  # 3D
TEMPERATURE_PERTURBATION = os.getenv('T', 'T')  # 4D
SKIN_TEMPERATURE = os.getenv('TSK', 'TSK')  # 3D
SURFACE_PRESSURE = os.getenv('SURFACE_PRESSURE', 'PSFC')  # 3D
SENSIBLE_HEAT = os.getenv('SENSIBLE_HEAT', 'HFX')  # 3D
LATENT_HEAT = os.getenv('LATENT_HEAT', 'LH')  # 3D
SPECIFIC_HUMIDITY = os.getenv('SPECIFIC_HUMIDITY', 'QVAPOR')  # 4D
SURFACE_TEMPERATURE = os.getenv('SURFACE_TEMPERATURE', 'T2')  # 3D
CLOUD_MIXING_RATIO = os.getenv('CLOUD_MIXING_RATIO', 'QCLOUD')  # 4D
PRESSURE_PERTURBATION = os.getenv('PRESSURE_PERTURBATION', 'P')  # 4D
BASE_PRESSURE = os.getenv('BASE_PRESSURE', 'PB')  # 4D
CONVECTIVE_RAIN = os.getenv('CONVECTIVE_RAIN', 'RAINC')  # 3D
NON_CONVECTIVE_RAIN = os.getenv('NON_CONVECTIVE_RAIN', 'RAINNC')  # 3D
SOLAR_RADIATION = os.getenv('SOLAR_RADIATION', 'SWDOWN')
P_TOP = os.getenv('P_TOP', 'P_TOP')  # 1D
T_ISO = os.getenv('T_ISO', 'TISO')  # 1D
P_00 = os.getenv('P_00', 'P00')  # 1D
T_00 = os.getenv('T_00', 'T00')  # 1D
TLP = os.getenv('TLP', 'TLP')  # 1D
TERRAIN_HEIGHT = os.getenv('TERRAIN_HEIGHT', 'HGT')  # 2D
ZNU = os.getenv('ZNU', 'ZNU')  # 2D

#######################
# DATABASE COLUMN NAMES
#######################
CO_COLUMN = os.getenv('CO_COLUMN', 'co')
NO_COLUMN = os.getenv('NO_COLUMN', 'no')
NO2_COLUMN = os.getenv('NO2_COLUMN', 'no2')
O3_COLUMN = os.getenv('O3_COLUMN', 'o3')
PM10_COLUMN = os.getenv('PM10_COLUMN', 'pm10')
PM25_COLUMN = os.getenv('PM25_COLUMN', 'pm25')

###########################
# Copert parameters files #
###########################
file_root = os.path.dirname(os.path.abspath(__file__))
PC_FILE = os.path.join(file_root, "copert/copert_params/PC_parameter.csv")
LDV_FILE = os.path.join(file_root, "copert/copert_params/LDV_parameter.csv")
HDV_FILE = os.path.join(file_root, "copert/copert_params/HDV_parameter.csv")
MOTO_FILE = os.path.join(file_root, "copert/copert_params/Moto_parameter.csv")

#############
# Link data #
#############
N_TIMESTEPS = 1
SPEED = 40

######################
# Vehicle fleet data #
######################
ENGINE_CAPACITY_GASOLINE_LESS_1P4 = 0.599
ENGINE_CAPACITY_GASOLINE_1P4_TO_2P0 = 0.346
ENGINE_CAPACITY_GASOLINE_MORE_2 = 0.038
ENGINE_CAPACITY_DIESEL_LESS_1P4 = 0.098
ENGINE_CAPACITY_DIESEL_1P4_TO_2P0 = 0.778
ENGINE_CAPACITY_DIESEL_MORE_2 = 0.125
GASOLINE_PROPORTION = 0.292
PASSENGER_PROPORTION = 0.9

############################
# Proportion of pollutants #
############################
NO2_PROPORTION = 0.13
NO_PROPORTION = 0.87
PM10_PROPORTION = 0.675
PM25_PROPORTION = 0.325
