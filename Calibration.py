from API.d128_controller import D128Controller
import numpy as np

# Global variables
controller = D128Controller()

# Global paramters
# max_energy_area = xx

# Calibration paramters:
PW_min = 50             # µs
PW_max = 1000           # µs 
PW_increment = 50       # µs
RP_min = 10             # % 
RP_max = 100            # %
RP_increment = 10       # %
IP_min = 1              # µs
IP_max = 990            # µs 
IP_increment = 10       # µs

# Paramter arrays
PW_arr = np.arange(PW_min, PW_max, PW_increment) 
PR_arr = np.arange(RP_min, RP_max, RP_increment)
IP_arr = np.arange(IP_min, IP_max, IP_increment)

# Initialize the D128Controller


def init_DS8R ():
    # Open device and return status
    success, d128 = controller.D128ctrl('open')

    if success:
        print("Device opened successfully.")

        # Disable the device
        success, d128 = controller.D128ctrl('enable', d128, False)
        
        # Set paramters
        success, d128 = controller.D128ctrl('mode', d128, 'Bi-phasic')
        success, d128 = controller.D128ctrl('polarity', d128, 'Positive')
        success, d128 = controller.D128ctrl('source', d128, 'Internal')
        success, d128 = controller.D128ctrl('demand', d128, 5)
        success, d128 = controller.D128ctrl('pulsewidth', d128, 2000)
        success, d128 = controller.D128ctrl('dwell', d128, 1)
        success, d128 = controller.D128ctrl('recovery', d128, 100)

        # Upload all parameters to the device
        success = controller.D128ctrl('upload', d128)

        # Enable the device
        success, d128 = controller.D128ctrl('enable', d128, False)

        # Download status from device
        print('Do these paramters correspond to want appears on the device? \n')
        success, d128 = controller.D128ctrl('status', d128)
        print(d128)  # Display the current state

        # Close device (optional)
        # success = controller.D128ctrl('close', d128)
    else:
        print("Failed to open the device.")