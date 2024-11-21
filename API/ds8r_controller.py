# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# API for DS8R Digitimer Stimulator
import os
#from ctypes import Structure, c_ubyte, c_ushort, c_int, POINTER, WINFUNCTYPE, c_void_p, byref, WinDLL #, sizeof, cast
from ctypes import c_int, c_uint, c_void_p, Structure, Union, POINTER, WINFUNCTYPE, LittleEndianStructure, byref, WinDLL
import ctypes

ERROR_SUCCESS = {0, 1641, 3010, 3011}

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

class DS8RController:
    def __init__(self):
        self.PATH_PROXY = ''  
        self.NAME_PROXY = 'D128RProxy.dll'
        self.ALIAS_PROXY = 'D128RProxy'
        self.PATH_DLL = ''
        self.NAME_DLL = 'D128API.dll'

        # Maps for user-friendly names to actual values
        self.D128Mode = {
            'Mono-phasic': 1,
            'Bi-phasic': 2,
            'NoChange': 7
        }

        self.D128Pol = {
            'Positive': 1,
            'Negative': 2,
            'Alternating': 3,
            'NoChange': 7
        }

        self.D128Src = {
            'Internal': 1,
            'External': 2,
            'NoChange': 7
        }

        self.D128Enabled = {
            'True',
            'False',
            1,
            0
        }

        self.d128 = {
            'mode': 0,
            'polarity': 0,
            'source': 0,
            'demand': 0,
            'pulsewidth': 0,
            'dwell': 0,
            'recovery': 0,
            'enabled': 0
        }

        self.apiRef = c_int()          # Session reference
        self.retError = c_int()         # Initialization error
        self.retAPIError = c_int()      # General API error code
        #self.current_state = D188DEVICESTATE_T()  # Device state structure
        self.cbState = c_int()
        self.CurrentState = D128()      # Used to store current state retrived from DLL
        self.NewState = D128()          # Used to set new state through DLL

    def initialize(self):
        '''
        Initializes the device and the current state of the device
        '''
        if hasattr(self, 'lib_original'):
            self.apiRef = c_int(0)
            self.retError = self.lib_original.DGD128_Initialise(byref(self.apiRef), byref(self.retAPIError), None, None)
            # The first call is to simply fetch the size of the CurrentState structre which neesd to be allocated.
            if self.retError in ERROR_SUCCESS and self.retAPIError.value in ERROR_SUCCESS:
                self.retError = self.lib_original.DGD128_Update(self.apiRef, byref(self.retAPIError), None, 0, None, byref(self.cbState), None, None)
                print('initilization successful ;)')
            else:
                print('ERROR during initialization.')
                print('Didin''t initialize! retError = ', self.retError, ' retAPIError = ', self.retAPIError.value)
        else:
            print('D128 DLL not loaded. Cannot initilize.')

    def Close(self):
        if hasattr(self, 'lib_original'):
            if self.apiRef.value:
                #print('before closing, apiRef: ', self.apiRef.value)
                self.retError = self.lib_original.DGD128_Close(byref(self.apiRef), byref(self.retAPIError), None, None)
                #print('after closing, apiRef: ', self.apiRef.value)
            else:
                print('Didin''t close! retError = ', self.retError, ' apiRef = ', self.apiRef.value)
        else:
            print('D188 Proxy Library not loaded. Open command must be called first.')
        return True

    def Load(self):
        full_proxy = os.path.join(self.PATH_PROXY, self.NAME_PROXY)
        full_dll = os.path.join(self.PATH_DLL, self.NAME_DLL)

        try:
            self.lib = ctypes.WinDLL(full_proxy) 
            self.lib_original = ctypes.WinDLL(full_dll) 
            return True
        except OSError:
            print(f"{full_dll} or {full_proxy} was not found!")
            return False
        
    def Unload(self):
        if hasattr(self, 'lib_original'):
            ctypes.windll.kernel32.FreeLibrary(self.lib._handle)
            del self.lib
            print('proxy deleted')
        if hasattr(self, 'lib_original'):
            ctypes.windll.kernel32.FreeLibrary(self.lib_original._handle)
            del self.lib_original
            print('dll original deleted')

    def D128ctrl(self, command, *args):
        success = False
        if command.lower() == 'open':
            if len(args) == 0:
                success = self.Load()
                if success:
                    self.initialize()
                    self.d128.update({'mode': 0, 'polarity': 0, 'source': 0, 
                                      'demand': 0, 'pulsewidth': 0, 
                                      'dwell': 0, 'recovery': 0, 'enabled': 0})
            else:
                print("Unexpected number of arguments for open command. It accepts no arguments.")

        elif command.lower() == 'close':
            if len(args) == 1:
                # print('not implemented. useful to free resources') ### potential emprovement
                success = self.Close()
            else:
                print("Unexpected number of arguments for close command. It requires the d128 struct.")

        elif command.lower() == 'trigger':
            if len(args) == 1:
                self.Trigger()
                success = True
            else:
                print("Unexpected number of arguments for trigger command.")

        elif command.lower() == 'upload':
            if len(args) == 1:
                self.d128 = args[0]
                self.Set(self.d128)
                success = True
            else:
                print("Unexpected number of arguments for upload command. It requires the d128 struct.")

        elif command.lower() == 'status':
            if len(args) == 1:
                self.d128 = self.GetState(args[0])
                success = True
            else:
                print("Unexpected number of arguments for status command. It requires the d128 struct.")

        elif command.lower() == 'mode':
            if len(args) == 2:
                self.d128 = args[0]
                mode_str = args[1]
                if mode_str in self.D128Mode:
                    self.d128['mode'] = self.D128Mode[mode_str]
                else:
                    print(f'Unknown mode type {mode_str}')
                success = True
            else:
                print('Unexpected number of arguments for mode command')
                print('\td128 - D128 struct returned by open command')
                print('\tmode - ' + ', '.join(self.D128Mode.keys()))

        elif command.lower() == 'polarity':
            if len(args) == 2:
                self.d128 = args[0]
                pol_str = args[1]
                if pol_str in self.D128Pol:
                    self.d128['polarity'] = self.D128Pol[pol_str]
                    success = True
                else:
                    print(f'Unknown polarity type {pol_str}')
            else:
                print('Unexpected number of arguments for polarity command')
                print('\td128 - D128 struct returned by open command')
                print('\tpolarity - ' + ', '.join(self.D128Pol.keys()))

        elif command.lower() == 'source':
            if len(args) == 2:
                self.d128 = args[0]
                src_str = args[1]
                if src_str in self.D128Src:
                    self.d128['source'] = self.D128Src[src_str]
                    success = True
                else:
                    print(f'Unknown source type {src_str}')
            else:
                print('Unexpected number of arguments for source command')
                print('\td128 - D128 struct returned by open command')
                print('\tsource - ' + ', '.join(self.D128Src.keys()))
        
        elif command.lower() == 'enable':
            if len(args) == 2:
                self.d128 = args[0]
                is_enabled = args[1]
                if is_enabled in self.D128Enabled:
                    if is_enabled:
                        self.d128['enabled'] = 1
                    else:
                        self.d128['enabled'] = 0
                    success = True
                else:
                    print(f'Unknown source type {is_enabled}')
            else:
                print('Unexpected number of arguments for enable command')
                print('\td128 - D128 struct returned by open command')
                print('\tenable - True or False (1 or 0)\n')

        elif command.lower() == 'demand':
            if len(args) == 2:
                self.d128 = args[0]
                pulse_amp = args[1]
                if 0 <= pulse_amp <= 1000 :
                    self.d128['demand'] = int(pulse_amp * 10)
                    success = True
                else:
                    print(f'Pulse amplitude out or range')
            else:
                print('Unexpected number of arguments for demand command')
                print('\td128 - D128 struct returned by open command')
                print('\tdemand - float value between 0 and 1000. max one decimal point') 

        elif command.lower() == 'pulsewidth':
            if len(args) == 2:
                self.d128 = args[0]
                pulse_width = args[1]
                if 50 <= pulse_width <= 2000 :
                    self.d128['pulsewidth'] = pulse_width 
                    success = True
                else:
                    print(f'Pulse width out or range')
            else:
                print('Unexpected number of arguments for pulsewidth command')
                print('\td128 - D128 struct returned by open command')
                print('\tpulsewidth - integer value between 50 and 2000')

        elif command.lower() == 'dwell':
            if len(args) == 2:
                self.d128 = args[0]
                inter_pulse = args[1]
                if 1 <= inter_pulse <= 990 :
                    self.d128['dwell'] = inter_pulse 
                    success = True
                else:
                    print(f'Interpulse delay out or range')
            else:
                print('Unexpected number of arguments for dwell command')
                print('\td128 - D128 struct returned by open command')
                print('\tInterpulse delay - integer value between 1 and 990')

        elif command.lower() == 'recovery':
            if len(args) == 2:
                self.d128 = args[0]
                rec_percentage = args[1]
                if 10 <= rec_percentage <= 100 :
                    self.d128['recovery'] = rec_percentage 
                    success = True
                else:
                    print(f'recovery purcentage out or range [10%-100%]')
            else:
                print('Unexpected number of arguments for recovery command')
                print('\td128 - D128 struct returned by open command')
                print('\trecovery - integer value between 10 and 100')

        return success, self.d128

    def Trigger(self):
        if hasattr(self, 'lib'):
            self.lib.DGD128_Trigger()
        else:
            print('D128 Proxy Library not loaded. Open command must be called first.')

    def Set(self, d128):
        if hasattr(self, 'lib'):
            print(d128) # to be deleted
            self.lib.DGD128_Set(
                d128['mode'], d128['polarity'], d128['source'], 
                d128['demand'], d128['pulsewidth'], d128['dwell'], 
                d128['recovery'], d128['enabled']
            )
        else:
            print('D128 Proxy Library not loaded. Open command must be called first.')

    def GetState(self, d128):
        if hasattr(self, 'lib'):
            # Assuming these functions take ctypes pointers to receive values
            mode = ctypes.c_int()
            pol = ctypes.c_int()
            source = ctypes.c_int()
            demand = ctypes.c_int() 
            pw = ctypes.c_int()
            dwell = ctypes.c_int()
            recovery = ctypes.c_int()
            enabled = ctypes.c_int()

            self.lib.DGD128_Get(ctypes.byref(mode), ctypes.byref(pol), 
                                ctypes.byref(source), ctypes.byref(demand), 
                                ctypes.byref(pw), ctypes.byref(dwell), 
                                ctypes.byref(recovery), ctypes.byref(enabled))

            return {
                'mode': mode.value,
                'polarity': pol.value,
                'source': source.value,
                'demand': demand.value,
                'pulsewidth': pw.value,
                'dwell': dwell.value,
                'recovery': recovery.value,
                'enabled': enabled.value
            }
        else:
            print('D128 Proxy Library not loaded. Open command must be called first.')
            return d128



if __name__ == '__main__':
    # Example usage
    controller = DS8RController()
    success, d128 = controller.D128ctrl('open')
        
    if success:
        print("Device opened successfully.")
    else:
        print("Failed to open the device.")

    controller.initialize()

        # Set paramters
    success, d128 = controller.D128ctrl('mode', d128, 'Bi-phasic')
    success, d128 = controller.D128ctrl('polarity', d128, 'Positive')
    success, d128 = controller.D128ctrl('source', d128, 'Internal')
    success, d128 = controller.D128ctrl('demand', d128, 3)
    success, d128 = controller.D128ctrl('pulsewidth', d128, 500)
    success, d128 = controller.D128ctrl('dwell', d128, 500)
    success, d128 = controller.D128ctrl('recovery', d128, 60)

    # Enable the device
    success, d128 = controller.D128ctrl('enable', d128, True)

    # Upload all parameters to the device
    success = controller.D128ctrl('upload', d128)

    # Download status from device
    success, d128 = controller.D128ctrl('status', d128)

    controller.Close()
    print('closed')