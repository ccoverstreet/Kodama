from adafruit_servokit import ServoKit

import board
from adafruit_pca9685 import PCA9685
#i2c = board.I2C()
#pca = PCA9685(i2c)

#pca.frequency = 60

kit = ServoKit(channels=16)
print(dir(kit), dir(kit._pca))
kit._pca.channels[15].duty_cycle = 0xFFFF

#pca.channels[15].dutycycle=0xFFFF

kit.servo[15].throttle = -1
