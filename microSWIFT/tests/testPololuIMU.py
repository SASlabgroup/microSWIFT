#!/usr/bin/python
#This code was written by Caleb G. Teague in 2017

"""To do:
	Add more error handling?
	Add more variable setup on initiation
	Update the timing for my accurate polling
	Create getYaw() and getAngle() functions
"""	

import smbus
import time
import math
import thread

class MinIMU_v5_pi:
	#aScale = 2g/2^15, gScale = 500dps/2^15, mScale = 4guass/2^15
	#You only need to change the scales if you change the settings in the enable functions, 
	#which this class is not yet setup to do...
	def __init__(self, SMBusNum = 1, aScale = 2*9.806/32768, gScale = 500.0/32768, mScale = 4.0/32768):

		#Accelerometer and Gyro Register addresses
		self.Accel_Gyro_REG = dict(  \
		FUNC_CFG_ACCESS 	= 0x01, \
									\
		FIFO_CTRL1      	= 0x06, \
		FIFO_CTRL2      	= 0x07, \
		FIFO_CTRL3      	= 0x08, \
		FIFO_CTRL4      	= 0x09, \
		FIFO_CTRL5      	= 0x0A, \
		ORIENT_CFG_G    	= 0x0B, \
									\
		INT1_CTRL       	= 0x0D, \
		INT2_CTRL       	= 0x0E, \
		WHO_AM_I        	= 0x0F, \
		CTRL1_XL        	= 0x10, \
		CTRL2_G         	= 0x11, \
		CTRL3_C         	= 0x12, \
		CTRL4_C         	= 0x13, \
		CTRL5_C         	= 0x14, \
		CTRL6_C         	= 0x15, \
		CTRL7_G         	= 0x16, \
		CTRL8_XL        	= 0x17, \
		CTRL9_XL        	= 0x18, \
		CTRL10_C        	= 0x19, \
									\
		WAKE_UP_SRC     	= 0x1B, \
		TAP_SRC         	= 0x1C, \
		D6D_SRC         	= 0x1D, \
		STATUS_REG      	= 0x1E, \
									\
		OUT_TEMP_L      	= 0x20, \
		OUT_TEMP_H      	= 0x21, \
		OUTX_L_G        	= 0x22, \
		OUTX_H_G        	= 0x23, \
		OUTY_L_G        	= 0x24, \
		OUTY_H_G        	= 0x25, \
		OUTZ_L_G        	= 0x26, \
		OUTZ_H_G        	= 0x27, \
		OUTX_L_XL       	= 0x28, \
		OUTX_H_XL       	= 0x29, \
		OUTY_L_XL       	= 0x2A, \
		OUTY_H_XL       	= 0x2B, \
		OUTZ_L_XL       	= 0x2C, \
		OUTZ_H_XL       	= 0x2D, \
									\
		FIFO_STATUS1    	= 0x3A, \
		FIFO_STATUS2    	= 0x3B, \
		FIFO_STATUS3    	= 0x3C, \
		FIFO_STATUS4    	= 0x3D, \
		FIFO_DATA_OUT_L 	= 0x3E, \
		FIFO_DATA_OUT_H 	= 0x3F, \
		TIMESTAMP0_REG  	= 0x40, \
		TIMESTAMP1_REG  	= 0x41, \
		TIMESTAMP2_REG  	= 0x42, \
									\
		STEP_TIMESTAMP_L	= 0x49, \
		STEP_TIMESTAMP_H	= 0x4A, \
		STEP_COUNTER_L  	= 0x4B, \
		STEP_COUNTER_H  	= 0x4C, \
									\
		FUNC_SRC        	= 0x53, \
									\
		TAP_CFG         	= 0x58, \
		TAP_THS_6D      	= 0x59, \
		INT_DUR2        	= 0x5A, \
		WAKE_UP_THS     	= 0x5B, \
		WAKE_UP_DUR     	= 0x5C, \
		FREE_FALL      		= 0x5D, \
		MD1_CFG         	= 0x5E, \
		MD2_CFG         	= 0x5F  )

		#Magnemometer addresses
		self.Mag_REG= dict( \
		WHO_AM_I    = 0x0F, \
							\
		CTRL_REG1   = 0x20, \
		CTRL_REG2   = 0x21, \
		CTRL_REG3   = 0x22, \
		CTRL_REG4   = 0x23, \
		CTRL_REG5   = 0x24, \
							\
		STATUS_REG  = 0x27, \
		OUT_X_L     = 0x28, \
		OUT_X_H     = 0x29, \
		OUT_Y_L     = 0x2A, \
		OUT_Y_H     = 0x2B, \
		OUT_Z_L     = 0x2C, \
		OUT_Z_H     = 0x2D, \
		TEMP_OUT_L  = 0x2E, \
		TEMP_OUT_H  = 0x2F, \
		INT_CFG     = 0x30, \
		INT_SRC     = 0x31, \
		INT_THS_L   = 0x32, \
		INT_THS_H   = 0x33  )
				
		#Unit scales
		self.aScale = aScale
		self.gScale = gScale
		self.mScale = mScale
		
		#Variables for updateAngle and updateYaw
		self.prevAngle = [[0,0,0]] #x, y, z (roll, pitch, yaw)
		self.prevYaw = [0]
		self.tau = 0.04 #Want this roughly 10x the dt
		self.lastTimeAngle = [0]
		self.lastTimeYaw = [0]
	
		#i2c addresses
		self.mag = 0x1d #0011110 (from docs)
		self.accel_gyro = 0x6b

		#Connect i2c bus
		self.bus = smbus.SMBus(SMBusNum)
		
		#Enable Mag, Accel, and Gyro
		self.enableMag()
		self.enableAccel_Gyro()
		

	"""Setup the needed registers for the Accelerometer and Gyro"""
	def enableAccel_Gyro(self):
		#Accelerometer

		#default: 0b10000000
		#ODR = 1.66 kHz; +/-2g; BW = 400Hz
		self.bus.write_byte_data(self.accel_gyro, self.Accel_Gyro_REG['CTRL1_XL'], 0b10000000)

		#Gyro

		#default: 0b010000000
		#ODR = 1.66 kHz; 500dps
		self.bus.write_byte_data(self.accel_gyro, self.Accel_Gyro_REG['CTRL2_G'], 0b10000100)

		#Accelerometer and Gyro

		#default: 0b00000100
		#IF_INC = 1 (automatically increment register address)
		self.bus.write_byte_data(self.accel_gyro, self.Accel_Gyro_REG['CTRL3_C'], 0b00000100)

	"""Setup the needed registers for the Magnetometer"""
	def enableMag(self):
		#Magnemometer        

		#default: 0b01110000
		#Temp off, High-Performance, ODR = 300Hz, Self_test off
		self.bus.write_byte_data(self.mag, self.Mag_REG['CTRL_REG1'], 0b01010010)
		
		#default: 0b00000000
		# +/-4guass, reboot off, soft_reset off
		self.bus.write_byte_data(self.mag, self.Mag_REG['CTRL_REG2'], 0b00000000)        

		#default: 0b00000011
		#Low-power off, default SPI, continous convo mode
		self.bus.write_byte_data(self.mag, self.Mag_REG['CTRL_REG3'], 0b00000000)

		#default: 0b00000000
		#High-Performance, data LSb at lower address
		self.bus.write_byte_data(self.mag, self.Mag_REG['CTRL_REG4'], 0b00001000)

	"""Read values from accelerometer and scale them to m/s^2, returns 0's if unable to read"""
	def readAccelerometer(self):
		#   Reading low and high 8-bit register and converting the 16-bit
		#two's complement number to decimal.
		try:
			AX = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTX_L_XL']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTX_H_XL']))

			AY = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTY_L_XL']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTY_H_XL']))

			AZ = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTZ_L_XL']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTZ_H_XL']))
		except:
			#print "Error!"
			return 0, 0, 0

		#Scaling the decimal number to understandable units
		AX *= self.aScale; AY *= self.aScale; AZ *= self.aScale;
						   
		return [AX, AY, AZ]

	"""Read values from gyro and scale them to dps, returns 0's if unable to read"""
	def readGyro(self):
		#   Reading low and high 8-bit register and converting the 16-bit
		#two's complement number to decimal.
		try:
			GX = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTX_L_G']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTX_H_G']))

			GY = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTY_L_G']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTY_H_G']))

			GZ = self.byteToNumber(self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTZ_L_G']), \
									self.bus.read_byte_data(self.accel_gyro, self.Accel_Gyro_REG['OUTZ_H_G']))
		except:
			#print "Error!"
			return 0, 0, 0
			
		#Scaling the decimal number to understandable units
		GX *= self.gScale; GY *= self.gScale; GZ *= self.gScale;
		
		return [GX, GY, GZ]

	"""Read values from magnetometer and scale them to guass, returns 0's if unable to read"""
	def readMagnetometer(self):
		#   Reading low and high 8-bit register and converting the 16-bit
		#two's complement number to decimal.
		try:
			MX = self.byteToNumber(self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_X_L']), \
									self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_X_H']))

			MY = self.byteToNumber(self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_Y_L']), \
									self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_Y_H']))

			MZ = self.byteToNumber(self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_Z_L']), \
									self.bus.read_byte_data(self.mag, self.Mag_REG['OUT_Z_H']))
		except:
			#print "Error!"
			return 0, 0, 0

		#Scaling the decimal number to understandable units
		MX *= self.mScale; MY *= self.mScale; MZ *= self.mScale; 

		return [MX, MY, MZ]

	"""Combines Hi and Low 8-bit values to a 16-bit two's complement and
	converts to decimal"""
	def byteToNumber(self, val_Low, val_Hi):
		number = 256 * val_Hi + val_Low #2^8 = 256
		if number >= 32768: #2^7 = 32768
			number= number - 65536 #For two's complement
		return number
	 
	 
	
	"""updateAngle() uses readAccelerometer(), readGyro(), readMagnetometer() to find the current roll,
	pitch, and yaw of the IMU with a complementaty filter.  It requires the global variables tau,
	prevAngle, and lastTimeAngle to exist as well."""
	def updateAngle(self):
		[Ax, Ay, Az] = self.readAccelerometer()
		[Gx_w, Gy_w, Gz_w] = self.readGyro()
		[Mx, My, Mz] = self.readMagnetometer()

		if self.lastTimeAngle[0] == 0: #If this is the first time using updatePos
			self.lastTimeAngle[0] = time.time()

		#Find the angle change given by the Gyro
		dt = time.time() - self.lastTimeAngle[0]    
		Gx = self.prevAngle[0][0] + Gx_w * dt
		Gy = self.prevAngle[0][1] + Gy_w * dt
		Gz = self.prevAngle[0][2] + Gz_w * dt

		#Using the Accelerometer find pitch and roll
		rho = math.degrees(math.atan2(Ax, math.sqrt(Ay**2 + Az**2))) #pitch
		phi = math.degrees(math.atan2(Ay, math.sqrt(Ax**2 + Az**2))) #roll

		#Using the Magnetometer find yaw
		theta = math.degrees(math.atan2(-1*My, Mx)) + 180 #yaw

		#To deal with modular angles in a non-modular number system I had to keep
		#the Gz and theta values from 'splitting' where one would read 359 and
		#other 1, causing the filter to go DOWN from 359 to 1 rather than UP.  To
		#accomplish this this I 'cycle' the Gz value around to keep the
		#complementaty filter working.
		if Gz - theta > 180:
			Gz = Gz - 360
		if Gz - theta < -180:
			Gz = Gz + 360

		#This must be used if the device wasn't laid flat
		#theta = math.degrees(math.atan2(-1*My*math.cos(rho) + Mz*math.sin(phi), Mx*math.cos(rho) + My*math.sin(rho)*math.sin(phi) + Mz*math.sin(rho)*math.cos(phi)))

		#This combines a LPF on phi, rho, and theta with a HPF on the Gyro values
		alpha = self.tau/(self.tau + dt)
		xAngle = (alpha * Gx) + ((1-alpha) * phi)
		yAngle = (alpha * Gy) + ((1-alpha) * rho)
		zAngle = (alpha * Gz) + ((1-alpha) * theta)

		#Update previous angle with the current one
		self.prevAngle[0] = [xAngle, yAngle, zAngle]

		#Update time for dt calculations
		self.lastTimeAngle[0] = time.time()

		return xAngle, yAngle, zAngle #roll, pitch, yaw

	"""updateYaw() uses readGyro() and readMagnetometer() to find the current yaw of the
	IMU with a complementaty filter.  It requires the global variables tau,	prevYaw, 
	and lastTimeYaw to exist as well."""
	def updateYaw(self):
		[Gx_w, Gy_w, Gz_w] = self.readGyro()
		[Mx, My, Mz] = self.readMagnetometer()

		if self.lastTimeYaw[0] == 0: #If this is the first time using updatePos
			self.lastTimeYaw[0] = time.time()

		#Find the angle change given by the Gyro
		dt = time.time() - self.lastTimeYaw[0]
		Gz = self.prevYaw[0] + Gz_w * dt

		#Using the Magnetometer find yaw
		theta = math.degrees(math.atan2(-1*My, Mx)) + 180 #yaw

		#To deal with modular angles in a non-modular number system I had to keep
		#the Gz and theta values from 'splitting' where one would read 359 and
		#other 1, causing the filter to go DOWN from 359 to 1 rather than UP.  To
		#accomplish this this I 'cycle' the Gz value around to keep the
		#complementaty filter working.
		if Gz - theta > 180:
			Gz = Gz - 360
		if Gz - theta < -180:
			Gz = Gz + 360

		#This combines a LPF on phi, rho, and theta with a HPF on the Gyro values
		alpha = self.tau/(self.tau + dt)
		zAngle = (alpha * Gz) + ((1-alpha) * theta)

		#Update previous yaw with the current one
		self.prevYaw[0] = zAngle

		#Update time for dt calculations
		self.lastTimeYaw[0] = time.time()

		return zAngle
		
	"""Creates another thread which calls updateAngle every 4ms (250Hz) to track the
	current roll, pitch, and yaw"""
	def trackAngle(self):
		thread.start_new_thread(self.trackAngleThread, ())
	
	def trackAngleThread(self):
		while True:
			self.updateAngle()
			time.sleep(0.004)
			
	"""Creates another thread which calls updateYaw every 4ms (250Hz) to track the
	current yaw"""
	def trackYaw(self):
		thread.start_new_thread(self.trackYawThread, ())
	
	def trackYawThread(self):
		while True:
			self.updateYaw()
			time.sleep(0.004)

			
def main():
        IMU = MinIMU_v5_pi()

        IMU.trackYaw()
        '''while True:
                print IMU.prevYaw[0]
                time.sleep(0.1)'''

        while True:
                i = 0
                while i < 30:
                    i += 1
                    IMU.updateYaw()
                    time.sleep(0.004)           
                print IMU.prevYaw[0]
                print  IMU.readAccelerometer() + IMU.readGyro() + IMU.readMagnetometer()
                time.sleep(0.004)


if __name__ == "__main__":
    print "MinIMU is main"
    main()
    