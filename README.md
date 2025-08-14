# Kodama 

Kodama is a home robot intended to allow for control via IP. This project is mostly a testbed for robotics/integration.

## Version 1

### Parts

- Raspberry Pi Model 4B
- Raspberry Pi Camera Module 3 - 12MP 120 Degree Wide Angle Lens 
- Adafruit 16 channel PWM/servo board for Raspberry Pi 
- Continuous Rotation Servo - FeeTech FS5103R 
- Continuous Rotation Servo Wheel 
- Microservo for camera tilt
- 3D printed chassis and components
- USB battery bank with 2 outputs for power supply
    - USB pigtail used to connect to 5V and ground pins and supply the servos with power

### Software

- Multiple Python-based web servers/socket servers to handle video stream, control communications, and serving of web interface.
    - Web and control servers could be integrated in the future. Separate for simplicity
- Current streaming method is to use Python with the rpicamera2 library to stream an MJPG to frontend

## Software Setup

- Mount RPi's filesystem using sshfs and use `upload_changes.sh` script to transfer necessary files over to the pi
- Run the `install.sh` script on the pi to copy service files to the system directory, enable, and start the required services
