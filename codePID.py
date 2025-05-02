import time
import board
import busio
import pwmio
import random
import gc
import adafruit_vl53l0x  # Needed if using laser range finder
from analogio import AnalogIn
#import gc

############### CONSTANTS  ######################
# A few constants we'll use later
dt = 0.1 # sample interval
"Edit Frame Below for Steps"

"Enter steady state conditions"
time_step = 1000
freq = 750

## Set controller constants
Kc = -0.285 #Add code or value here###  ## Controller gain in MV/CV units (% of MV range/frac of CV range)
Ti = 29.75 ###Add code or value here###  ## Integral time
Td = 0 ###Add code or value here###  ## Derivative time
weight = 0.2
#Initialize variables needed for control calculation
SPinit = 200 ###Add code or value here###    # initial setpoint (fraction between CVMeasMin and CVMeasMax)
SP = SPinit
CV = SP      # set the initial value of CV to the SP

e, e1, e2 = 0, 0, 0   #error signals
t_old = 0   # prior time
MV = 50  #manipulated variable: % duty cycle for final control element (LED light) - pump, fan, etc.
MV1 = MV  #previous MV value
duty = 50  # MV duty cycle value sent to analog pin (must be between 0 and 65535);


#################################################
# Initialize variables
n = 0 # step number counter
PWM = 0     # output pwmf
tic = time.monotonic()  #get the initial time
y = 0

# Create the I2C interface.

i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
Ai0 = AnalogIn(board.A0)
usingRange = True
SensorN = 1 #1 = laser range finder
pwmOut = pwmio.PWMOut(board.D10, frequency=freq, duty_cycle=0)

TIM = 0


duty = MV/100*65535  # calculate the duty cycle value to send to the system input (MV pin)
pwmOut.duty_cycle = int(duty) # send the duty cycle as an integer value to the MV pin
CVinit= vl53.range # sensor value in fraction of range
CVraw = CVinit       #raw measurement from sensor (light sensor) in V
CVfilt = CVinit      #filtered measurement from sensor (light sensor) in V (the raw measurment will be put through a low pass filter)
CV = CVinit          #sensor measurement in fraction of range
CV1 = CVinit      #previous sensor measurement from 1 iteration ago
CV2 = CVinit  #previous sensor measurement from 2 iterations ago

time.sleep(dt)
safety = True
ticc = time.monotonic()
ticcc = ticc
while (safety == True):
    try:
        time.sleep(dt)
    except:
        continue
    #print('loop start')
    try:
     #   print('trying to read')
        CVraw = vl53.range #range in mm
        CVfilt = (1.0-weight)*CVfilt  + weight * CVraw # filtered sensor value in V
        CV = CVfilt
        e = SP-CV ###Add code or value here###
    #  print('read')
     #   print('1')

        try:
            tocc = time.monotonic()
            dtt = tocc - ticc
            ## Calculate the PID output (MV) using the velocity form of the digital PID equation
            Prop = e - e1 ###Add code or value here###  #Calculate the proportional part
            Int = dtt*e/Ti ###Add code or value here### #Calculate the integral part
            Der = Td/dtt*(CV-2*CV1+CV2)###Add code or value here### #Calculate the derivative part
            #print('3')
            dMV = Kc*(Prop+Int-Der)###Add code or value here###  #Put it all together to calculate the change in MV
            #print(dMV)
            ticc = time.monotonic()
            MV += dMV###Add code or value here###  #Calculate the MV value by adding the change in MV to the previous MV value
            #print('4')
            if (MV<20):
                MV = 20 ###Add code or value here### #cannot have an MV that's less than 0
            if (MV>100):
                MV = 100###Add code or value here### #cannot have an MV that's more than 100
            duty = MV/100*65535  # calculate the duty cycle value to send to the system input (MV pin)
            pwmOut.duty_cycle = int(duty) # send the duty cycle as an integer value to the MV pin
            #print('5')
                ## Update the past error and CV values
            e1 = e
            CV2 = CV1
            CV1 = CV
            #print('6')
                ## Print values

            print("{{ 'CV':{0:f}, 'MV': {1:f}, 'SP': {2:f}}}".format(CV,MV,SP))
            # set SP value.  SPinit before the step_time and SPinit+dSP after step_time

            TIM = time.monotonic() - ticcc
            if (TIM>time_step):
                ticcc = time.monotonic()
                SP = random.randint(100,300)
            #print('7')

            #print(TIM)
            gc.collect()
        except:
            continue
    except:
        continue
print ('done')
