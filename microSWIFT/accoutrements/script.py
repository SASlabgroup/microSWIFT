from . import imu_module
from ..utils import configuration

config = configuration.Config('./microSWIFT/microSWIFT/config.txt')
imu = imu_module.IMU(config)

imu.checkout(1)
