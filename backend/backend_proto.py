from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

zero_offset = 0.05

kit.continuous_servo[12].throttle = 0.05
kit.continuous_servo[13].throttle = 0.05
