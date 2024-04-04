# Further Modifications
This page lists additional modifications we applied after the initial setup.

## Adjusting the Range for the Accelerometer
Due to unavailability, we were forced to use a different accelerometer for
our design, We used the model [LSM6DSOX](https://www.adafruit.com/product/4438).
In Adafruit's python code for this accelerator, the default range is already
twice that of the original module, +/-4g compared to +/-2g. However, we saw
some behaviour, where we wanted to try out a higher range. The maximum value
for this is +/-16g, but we decided to stay with +/-8g and collect more data
before we might change the range to the maximum value.

The only modification required are two lines in the python code:
```
diff --git a/IMU/recordIMU.py b/IMU/recordIMU.py
--- a/IMU/recordIMU.py
+++ b/IMU/recordIMU.py
@@ -20,6 +20,7 @@ import RPi.GPIO as GPIO
 # IMU sensor imports
 # import IMU.adafruit_fxos8700_microSWIFT
 # import IMU.adafruit_fxas21002c_microSWIFT
+from adafruit_lsm6ds import AccelRange
 from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
 from adafruit_lis3mdl import LIS3MDL
 
@@ -73,6 +74,7 @@ def recordIMU(end_time):
         # fxos = IMU.adafruit_fxos8700_microSWIFT.FXOS8700(i2c, accel_range=0x00)
         # fxas = IMU.adafruit_fxas21002c_microSWIFT.FXAS21002C(i2c, gyro_range=500)
         accel_gyro = LSM6DS(i2c)
+        accel_gyro.accelerometer_range = AccelRange.RANGE_8G
         mag = LIS3MDL(i2c)
         
         # Sleep to start recording at same time as GPS
```
### Operational Notes - How to upload this file
1. connect router to laptop as for reading out the data
2. setup laptop for password-less login to buoys (via ssh-key)
3. scp -P2233 recordIMU.py microswift@192.168.0.<#bouy>:microswift/microSWIFT/IMU

The new default of +/-8g fo rthe accelerator is uploaded in the github
repository.
