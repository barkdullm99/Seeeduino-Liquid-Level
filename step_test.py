import time
import board
import busio
import pwmio
import adafruit_vl53l0x  # Needed if using laser range finder
from analogio import AnalogIn

############### CONSTANTS  ######################
# A few constants we'll use later
dt = 2  # sample interval
"Edit Frame Below for Steps"
MV_percents = [90, 80, 90, 70, 50, 30, 50, 70, 90, 60, 30, 60, 90]
"Enter steady state conditions"
time_step = 720
freq = 500
#################################################
# Initialize variables
n = 0 # step number counter
PWM = 0     # output pwmf
tic = time.monotonic()  #get the initial time
y = 0
# Create the I2C interface.
PWM = 0     # output pwmf
tic = time.monotonic()  #get the initial time

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
Ai0 = AnalogIn(board.A0)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
usingRange = True
SensorN = 1 #1 = laser range finder
pwmOut = pwmio.PWMOut(board.D10, frequency=freq, duty_cycle=0)
time.sleep(dt)
nmax = len(MV_percents) - 1

TIME = 0

while (True):
    "Set MV"
    if (n>nmax):
        n = 0
    
    MV = MV_percents[n]
    duty = MV/100*65535
    pwmOut.duty_cycle = int(duty)
    "Get y"
    y = vl53.range #range in mm

    if (TIME>time_step):
        TIME = 0
        n +=1

    TIME += dt
    print("{{ 'y':{0:f}, 'MV': {1:f} }}".format(y,MV))
    time.sleep(dt) # wait for the sample time interval
