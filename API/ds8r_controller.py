# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# API for DS8R Digitimer Stimulator
import os
from ctypes import c_int, c_uint, c_void_p, Structure, Union, POINTER, WINFUNCTYPE, LittleEndianStructure, byref, WinDLL
import ctypes
import time

### Python implementation of a C-style API interface ###
# This section below defines the C-level functions within the DLL. It's based on the D128-Example code provided from Digitimer
ERROR_SUCCESS = {0, 1641, 3010, 3011} # full error list in winerror.h

class STATEFLAGS(Union):
    class _Bits(LittleEndianStructure):
        _fields_ = [
            ("OVERENERGY", c_uint, 1),
            ("HWERROR", c_uint, 1),
            ("reserved", c_uint, 30),
        ]
    _anonymous_ = ("bits",)
    _fields_ = [
        ("bits", _Bits),
        ("VALUE", c_int),
    ]

class CONTROLFLAGS(Union):
    class _Bits(LittleEndianStructure):
        _fields_ = [
            ("ENABLE", c_int, 2),
            ("MODE", c_int, 3),
            ("POLARITY", c_int, 3),
            ("SOURCE", c_int, 3),
            ("ZERO", c_int, 2),
            ("TRIGGER", c_int, 2),
            ("NOBUZZER", c_int, 2),
            ("RESERVED", c_int, 15),
        ]
    _anonymous_ = ("bits",)
    _fields_ = [
        ("bits", _Bits),
        ("VALUE", c_int),
    ]

class D128STATE(Structure):
    _fields_ = [
        ("CONTROL", CONTROLFLAGS),
        ("DEMAND", c_int),
        ("WIDTH", c_int),
        ("RECOVERY", c_int),
        ("DWELL", c_int),
        ("CPULSE", c_uint),
        ("COOC", c_uint),
        ("CTOOFAST", c_uint),
        ("FSTATE", STATEFLAGS),
    ]

class D128DEVICESTATE(Structure):
    _fields_ = [
        ("D128_DeviceID", c_int),
        ("D128_VersionID", c_int),
        ("D128_Error", c_int),
        ("D128_State", D128STATE),
    ]

class DEVHDR(Structure):
    _fields_ = [
        ("DeviceCount", c_int),
    ]

class D128(Structure):
    _fields_ = [
        ("Header", DEVHDR),
        ("State", D128DEVICESTATE),
    ]

PD128 = POINTER(D128)

# Callback functions
DGClientInitialiseProc = WINFUNCTYPE(None, c_int, c_void_p) # First None indicates that function return type is void
DGClientUpdateProc = WINFUNCTYPE(None, c_int, POINTER(D128), c_void_p)
DGClientCloseProc = WINFUNCTYPE(None, c_int, c_void_p)

# Key functions
DGD128_Initialise = WINFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int), DGClientInitialiseProc, c_void_p)
DGD128_Update = WINFUNCTYPE(c_int, c_int, POINTER(c_int), PD128, c_int, PD128, POINTER(c_int), DGClientUpdateProc, c_void_p)
DGD128_Close = WINFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int), DGClientCloseProc, c_void_p)

### API ###
# This API has been custom made at Institute of Neuroinformatics (INI) for out experiments
class DS8RController:
    def __init__(self):
        self.PATH_DLL = ''
        self.NAME_DLL = 'D128API.dll'

        self.apiRef = c_int()          # Session reference
        self.retError = c_int()         # Initialization error
        self.retAPIError = c_int()      # General API error code
        self.cbState = c_int()
        self.CurrentState = D128()      # Used to store current state retrived from DLL
        self.NewState = D128()          # Used to set new state through DLL

        # Maps for user-friendly names to actual values
        self.DS8RMode = {
            'Mono-phasic': 1,
            'Bi-phasic': 2,
            'NoChange': 7
        }

        self.DS8RPol = {
            'Positive': 1,
            'Negative': 2,
            'Alternating': 3,
            'NoChange': 7
        }

        self.DS8RSrc = {
            'Internal': 1,   # (front panel)
            'External': 2,   # (rear panel BNC analog input)
            'NoChange': 7
        }

        self.DS8REnabled = {
            True: 1,
            False: 0
        }

    def Load(self):
        '''
        Loads DLL library used for controlling the DS8R stimulator
        '''
        full_dll = os.path.join(self.PATH_DLL, self.NAME_DLL)
        try:
            self.lib = WinDLL(full_dll) 
            return True
        except OSError:
            print(f"{full_dll} was not found!") # or {full_proxy}
            return False
        
    def Unload(self):
        '''
        Unloads DLL library used for controlling the DS8R stimulator
        '''
        if hasattr(self, 'lib') and self.lib is not None:
            del self.lib
            self.lib = None
            print('DS8R DLL unloaded successfully.')
        else:
            print('DLL not loaded. Nothing to unload.')

    def Initialize(self):
        '''
        Initializes the device and the current state of the device
        '''
        if hasattr(self, 'lib'):
            self.apiRef = c_int(0)
            self.retError = self.lib.DGD128_Initialise(byref(self.apiRef), byref(self.retAPIError), None, None)
            # The first call is to simply fetch the size of the CurrentState structre which neesd to be allocated.
            if self.retError in ERROR_SUCCESS and self.retAPIError.value in ERROR_SUCCESS:
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), None, 0, None, byref(self.cbState), None, None)
                print('DS8R initilization successful ;)')
            else:
                print('ERROR during initialization.')
                print('Didin''t initialize! retError = ', self.retError, ' retAPIError = ', self.retAPIError.value)
        else:
            print('D128 DLL not loaded. Cannot initilize.')
    
    def GetState(self):
        '''
        Returns dictionary with state of the device
        '''
        if hasattr(self, 'lib'):
            self._Read_CurrentState()
            return {
                'mode': self.CurrentState.State.D128_State.CONTROL.MODE,
                'polarity': self.CurrentState.State.D128_State.CONTROL.POLARITY,
                'source': self.CurrentState.State.D128_State.CONTROL.SOURCE,
                'demand': self.CurrentState.State.D128_State.DEMAND,
                'pulsewidth': self.CurrentState.State.D128_State.WIDTH,
                'dwell': self.CurrentState.State.D128_State.DWELL,
                'recovery': self.CurrentState.State.D128_State.RECOVERY,
                'enabled': self.CurrentState.State.D128_State.CONTROL.ENABLE
            }
        else:
            print('DS8R Library not loaded. Open command must be called first.')
            return {}

    def _Read_CurrentState(self):
        '''
        Updates the state of the device stored in self.CurrentState variable. 
        This function is used internally and is not meant for the user
        '''
        if self.retError in ERROR_SUCCESS and self.retAPIError.value in ERROR_SUCCESS:
            self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), None, 0, byref(self.CurrentState), byref(self.cbState), None, None)
        else:
            print('ERROR! couldn''t update the DS8R. retError = ', self.retError, ' and retAPIError = ', self.retAPIError.value)

    def Mode(self, mode_str):
        if hasattr(self, 'lib'):
            if mode_str in self.DS8RMode:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.CONTROL.MODE = self.DS8RMode[mode_str]
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Unknown mode type {mode_str}')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Polarity(self, pol_str):
        '''
        Set the pulse polarity.
        Args:
            pol_str (string): from self.DS8RPol typedef
        '''
        if hasattr(self, 'lib'):
            if pol_str in self.DS8RPol:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.CONTROL.POLARITY = self.DS8RPol[pol_str]
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Unknown mode type {pol_str}')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Source(self, src_str):
        '''
        Set the source for the stimulus demand; USB or analog input.
        Args:
            src_str (string): from self.DS8RSrc typedef
        '''
        if hasattr(self, 'lib'):
            if src_str in self.DS8RSrc:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.CONTROL.SOURCE = self.DS8RSrc[src_str]
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Unknown mode type {src_str}')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Demand(self, value):
        '''
        Set amplitude
        Args:
            value (float): acceptable amplitude in [0-1000] mA with one decimal precision
        '''
        if hasattr(self, 'lib'):
            if 0 <= value <= 1000:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.DEMAND = int(value * 10) # function takes (mA * 10)
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Invalid amplitude value!')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Pulsewidth(self, value):
        '''
        Set pulsewidth. width of the first square in case of bi-phasic
        Args:
            value (int): acceptable pulsewidth in [50-2000] us 
        '''
        if hasattr(self, 'lib'):
            if 50 <= value <= 2000:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.WIDTH = int(value)
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Invalid pulsewidth value!')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Dwell(self, value):
        '''
        Set inter-pulse width. Controls the period between the end of the stimulus pulse and the start of the recovery pulse when BI-PHASIC mode is enabled.
        Args:
            value (int): acceptable interpulse width in [1-990] us 
        '''
        if hasattr(self, 'lib'):
            if 1 <= value <= 990:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.DWELL = int(value)
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Invalid interpulse value!')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Recovery(self, value):
        '''
        Controls the recovery pulse duration when the BI-PHASIC mode is selected. The value represents the percentage 
        Amplitude the recovery pulse will have. The recovery pulse duration is automatically adjusted to ensure the 
        pulse energy is the same as the stimulus pulse.
        Args:
            value (int): acceptable recovery phase value in [10-100] %
        '''
        if hasattr(self, 'lib'):
            if 10 <= value <= 100:
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.RECOVERY = int(value)
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Invalid recovery value!')
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Enable(self, enabled):
        '''
        Control of output enable state.
        Args:
            enabled (bool)
        '''
        if hasattr(self, 'lib'):
            if isinstance(enabled, bool):
                self._Read_CurrentState()
                self.NewState = self.CurrentState
                self.NewState.State.D128_State.CONTROL.ENABLE = self.DS8REnabled[enabled]
                self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print(f'Unknown mode type {enabled}')
        else:
            print('DS8R Library not loaded. Open command must be called first.')
    
    def Cmd(self, command, *args):
        '''
        This function just provides a different format for calling the previous functions:
        Mode, Polarity, Source, Demand, Pulsewidth, Dwell, Recovery
        Args:
            command (string): different commands
            *args: different possible values depending on the command
        '''
        if command.lower() == 'mode':
            if len(args) == 1:
                mode_str = args[0]
                self.Mode(mode_str)
            else:
                print('Unexpected number of arguments for mode command')
                print('\tmode - ' + ', '.join(self.DS8RMode.keys()))

        elif command.lower() == 'polarity':
            if len(args) == 1:
                pol_str = args[0]
                self.Polarity(pol_str)
            else:
                print('Unexpected number of arguments for polarity command')
                print('\tpolarity - ' + ', '.join(self.DS8RPol.keys()))

        elif command.lower() == 'source':
            if len(args) == 1:
                src_str = args[0]
                self.Source(src_str)
            else:
                print('Unexpected number of arguments for source command')
                print('\tsource - ' + ', '.join(self.DS8RSrc.keys()))

        elif command.lower() == 'demand':
            if len(args) == 1:
                pulse_amp = args[0]
                self.Demand(pulse_amp)
            else:
                print('Unexpected number of arguments for demand command')
                print('\tdemand - float value between 0 and 1000. max one decimal point') 

        elif command.lower() == 'pulsewidth':
            if len(args) == 1:
                pulse_width = args[0]
                self.Pulsewidth(pulse_width)
            else:
                print('Unexpected number of arguments for pulsewidth command')
                print('\tpulsewidth - integer value between 50 and 2000')

        elif command.lower() == 'dwell':
            if len(args) == 1:
                inter_pulse = args[0]
                self.Dwell(inter_pulse)
            else:
                print('Unexpected number of arguments for dwell command')
                print('\tInterpulse delay - integer value between 1 and 990')

        elif command.lower() == 'recovery':
            if len(args) == 1:
                rec_percentage = args[0]
                self.Recovery(rec_percentage)
            else:
                print('Unexpected number of arguments for recovery command')
                print('\trecovery - integer value between 10 and 100')

    def Trigger(self):
        '''
        Triggers one time. TRIGGER is 0 in idle. Setting it to 1 triggers. After triggering it will be set back to zero automatically by the device 
        REMARK: Max trigger at 10Hz using USB, otherwise can have bugs
        '''
        if hasattr(self, 'lib'):
            self._Read_CurrentState()
            self.NewState = self.CurrentState
            self.NewState.State.D128_State.CONTROL.TRIGGER = 1
            self.retError = self.lib.DGD128_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
        else:
            print('DS8R Library not loaded. Open command must be called first.')

    def Close(self):
        '''
        Closes and disconnects from the underlying device management services. Frees resources and invalidates the 
        reference. Continuing to use the reference will result in returned errors.
        Once called, if there are no remaining clients connected to the underlying device services, they will automatically 
        close, freeing all communications resources used.
        '''
        if hasattr(self, 'lib'):
            if self.apiRef.value:
                #self.SetMode('OFF')
                self.retError = self.lib.DGD128_Close(byref(self.apiRef), byref(self.retAPIError), None, None)
                print('closed successfully.')
            else:
                print('DS8R Didin''t close! retError = ', self.retError, ' apiRef = ', self.apiRef.value)
        else:
            print('DS8R Library not loaded. Open command must be called first.')


if __name__ == '__main__':
    # Example usage
    controller = DS8RController()

    controller.Load()
    controller.Initialize() 

    state = controller.GetState()
    print(state)

    controller.Mode('Bi-phasic')
    controller.Polarity('Negative')
    controller.Source('Internal')
    controller.Demand(3.5)
    controller.Pulsewidth(60)
    controller.Dwell(10)
    controller.Recovery(90)
    controller.Enable(True)
    
    state = controller.GetState()
    print(state)
    
    controller.Trigger()

    controller.Close()

    controller.Unload()
    print('Done')