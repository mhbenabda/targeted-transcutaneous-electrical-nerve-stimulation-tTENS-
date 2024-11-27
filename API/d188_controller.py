# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# API for D188 Digitimer Electrode Selector
import os
from ctypes import Structure, c_ubyte, c_ushort, c_int, POINTER, WINFUNCTYPE, c_void_p, byref, WinDLL #, sizeof, cast
import time

ERROR_SUCCESS = {0, 1641, 3010, 3011}

class D188STATE_T(Structure):
    _fields_ = [
        ("D188_Mode", c_ubyte),       # Mode: 0 = OFF, 1 = USB, 2 = TTL (1-8), 3 = TTL (4-8)
        ("D188_Select", c_ubyte),     # Select: 0 = All channels off, 1 = Channel 1, ..., 128 = Channel 8
        ("D188_Indicator", c_ubyte),  # Indicator: 0 = OFF, !0 = ON
        ("D188_Delay", c_ushort)      # Delay in 100us units between change detection and application
    ]

class D188DEVICESTATE_T(Structure):
    _fields_ = [
        ("D188_DeviceID", c_int),
        ("D188_VersionID", c_int),
        ("D188_Error", c_int),
        ("D188_State", D188STATE_T)
    ]

class DEVHDR(Structure):
    _fields_ = [
        ("DeviceCount", c_int)
    ]

class D188(Structure):
    _fields_ = [
        ("Header", DEVHDR),
        ("State", D188DEVICESTATE_T)  # Array size can be dynamically managed in Python
    ]

# Define pointer types for convenience
PD188 = POINTER(D188)

# Define callback functions prototypes
DGClientInitialiseProc = WINFUNCTYPE(None, c_int, c_void_p)
DGClientUpdateProc = WINFUNCTYPE(None, c_int, POINTER(D188), c_void_p)
DGClientCloseProc = WINFUNCTYPE(None, c_int, c_void_p)

# Define DLL functions prototypes for the API
DGD188_Initialise = WINFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int), DGClientInitialiseProc, c_void_p)
DGD188_Update = WINFUNCTYPE(c_int, c_int, POINTER(c_int), PD188, c_int, PD188, POINTER(c_int), DGClientUpdateProc, c_void_p)
DGD188_Close = WINFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int), DGClientCloseProc, c_void_p)


class D188Controller:
    '''
    D188_Mode
        0 = OFF
        1 = Controlled by commands from USB (PC API)
        2 = 1 to 8 control from rear panel connector (TTL)
        3 = 4 to 8 control from rear panel connector (TTL)

    D188_Select
        0 = All channels off
        1 = Channel 1 selected
        2 = Channel 2 selected
        4 = Channel 3 selected
        8 = Channel 4 selected
        16 = Channel 5 selected
        32 = Channel 6 selected
        64 = Channel 7 selected
        128 = Channel 8 selected

        Only the first BIT set will enable a channel, subsequent set bits are ignored

    D188_Indicator
        0 = Channel active indicators OFF
        !0 = Channel active indicators ON

    D188_Delay
        n = number of 100us to delay between detecting a change on the rear panel socket and applying the change to the selected channels.
    '''
    def __init__(self):
        self.PATH_DLL = ''
        self.NAME_DLL = 'DGD188API.dll'

        self.apiRef = c_int(0)          # Session reference
        self.retError = c_int(0)         # Initialization error
        self.retAPIError = c_int(0)      # General API error code
        #self.current_state = D188DEVICESTATE_T()  # Device state structure
        self.cbState = c_int()
        self.CurrentState = D188()      # Used to store current state retrived from DLL
        self.NewState = D188()          # Used to set new state through DLL

        self.D188Mode = {
            'OFF': c_ubyte(0),
            'USB': c_ubyte(1),
            '8TTL': c_ubyte(2),
            '4TTL': c_ubyte(3)
        }

        self.D188Select = {
            0: c_ubyte(0),          # All channels off
            1: c_ubyte(1),          # Channel 1 selected
            2: c_ubyte(2),          # ...    
            3: c_ubyte(4),
            4: c_ubyte(8),
            5: c_ubyte(16),
            6: c_ubyte(32),
            7: c_ubyte(64),
            8: c_ubyte(128)
        }

        self.D188Indicator = {
            'OFF': c_ubyte(0),          # 0 = Channel active indicators OFF
            'ON': c_ubyte(1)           # !0 = Channel active indicators ON
        }
    '''
    def Open(self):
        success = False
        success = self.Load() # Load dll
        if success:
            try:
                self.Initialize()
            except AttributeError:
                print("Failed to Initialize D188!")
                exit(1)
    '''
    def Load(self):
        '''
        Loads dll library
        '''
        full_dll = os.path.join(self.PATH_DLL, self.NAME_DLL)
        try:
            self.lib = WinDLL(full_dll) 
            print('D188 load successful :)')
        except OSError:
            print(f"{full_dll} was not found!")
        
    def Initialize(self):
        '''
        Initializes the device and the current state of the device
        '''
        if hasattr(self, 'lib'):
            self.apiRef = c_int(0)
            self.retAPIError = c_int(0)
            self.retError = self.lib.DGD188_Initialise(byref(self.apiRef), byref(self.retAPIError), None, None)
            # The first call is to simply fetch the size of the CurrentState structre which neesd to be allocated.
            if self.retError in ERROR_SUCCESS and self.retAPIError.value in ERROR_SUCCESS:
                self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), None, 0, None, byref(self.cbState), None, None)
                print('D188 init successfully')
            else:
                print('ERROR during initialization.')
        else:
            print('D188 Proxy Library not loaded. Cannot initilize.')

    def GetState(self):
        '''
        Returns dictionary with state of the device
        '''
        if hasattr(self, 'lib'):
            #self.update_CurrentState()
            self.state = {
                'D188_Mode': self.CurrentState.State.D188_State.D188_Mode,
                'D188_Select': self.CurrentState.State.D188_State.D188_Select,
                'D188_Indicator': self.CurrentState.State.D188_State.D188_Indicator,
                'D188_Delay': self.CurrentState.State.D188_State.D188_Delay,
                'D188_DeviceID': self.CurrentState.State.D188_DeviceID,
                'D188_VersionID': self.CurrentState.State.D188_VersionID,
                'D188_Error': self.CurrentState.State.D188_Error,
                'DeviceCount': self.CurrentState.Header.DeviceCount
            }
            print(self.state)
            return self.state
        else:
            print('D188 Library not loaded. Open command must be called first.')
            return {}

    def update_CurrentState(self):
        '''
        Updates the state of the device stored in self.CurrentState variable
        '''
        if self.retError in ERROR_SUCCESS and self.retAPIError.value in ERROR_SUCCESS:
            self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), None, 0, byref(self.CurrentState), byref(self.cbState), None, None)
        else:
            print('ERROR! couldn''t update the D188. retError = ', self.retError, ' and retAPIError = ', self.retAPIError.value)

    def SetChannel(self, channel):
        '''
        Set which channel is active
        Args:
            channel (self.D1288Select): 0,1,2,...,8
        '''
        if hasattr(self, 'lib'):
            if channel in self.D188Select:
                self.update_CurrentState()
                if self.CurrentState.State.D188_State.D188_Mode == self.D188Mode['USB'].value:
                    self.NewState = self.CurrentState
                    self.NewState.State.D188_State.D188_Select = self.D188Select[channel]
                    self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
                    print('D188 channel update successfully')
                else:
                    print('Cannot set channel. You need to set USB mode first. ')
            else:
                print('Channel invalid')
        else:
            print('D188 Library not loaded. Open command must be called first.')

    def SetMode(self, mode):
        '''
        Set which controll mode is used for the selector
        Args:
            mode (self.D1288Mode): 'OFF', 'USB', '8TTL' or '4TTL'
        '''
        if hasattr(self, 'lib'):
            self.update_CurrentState()
            self.NewState = self.CurrentState
            self.NewState.State.D188_State.D188_Mode = self.D188Mode[mode]
            self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
        else:
            print('D188 Proxy Library not loaded. Open command must be called first.')

    def SetIndicator(self, indicator):
        '''
        Set if LED indicators are activated/disactivated
        Args:
            indicator (self.D1288Indicator): 'ON' or 'OFF'
        '''
        if hasattr(self, 'lib'):
            self.update_CurrentState()
            self.NewState = self.CurrentState
            self.NewState.State.D188_State.D188_Indicator = self.D188Indicator[indicator]
            self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
        else:
            print('D188 Proxy Library not loaded. Open command must be called first.')

    def SetDelay(self, delay):
        '''
        Set the The Delay/De-bounce setting
        D188_Delay DLL argument takes n = number of 100us to delay between detecting a change on the rear
        panel socket and applying the change to the selected channels.
        Args:
            delay (float): between 0.1-1000 milliseconds
        '''
        if hasattr(self, 'lib'):
            if 0.1 <= delay <= 1000:
                self.update_CurrentState()
                self.NewState = self.CurrentState
                n = int(delay * 1000 / 100)   # convert to us and devide by 100us to get n 
                c_n = c_ushort(n )   # devide by 100us to get n 
                self.NewState.State.D188_State.D188_Delay = c_n
                self.retError = self.lib.DGD188_Update(self.apiRef, byref(self.retAPIError), byref(self.NewState), self.cbState, byref(self.CurrentState), byref(self.cbState), None, None)
            else:
                print('ERROR! Delay out of range.')
        else:
            print('D188 Proxy Library not loaded. Open command must be called first.')

    def Close(self):
        '''
        Close connection with device
        '''
        if hasattr(self, 'lib'):
            if self.apiRef.value:
                #self.SetMode('OFF')
                self.retError = self.lib.DGD188_Close(byref(self.apiRef), byref(self.retAPIError), None, None)
                print('D188 closed successfully')
            else:
                print('Didin''t close! retError = ', self.retError, ' apiRef = ', self.apiRef.value)
        else:
            print('D188 Library not loaded. Open command must be called first.')


    def Unload(self):
        '''
        Unloads the DLL and frees resources.
        '''
        if hasattr(self, 'lib') and self.lib is not None:
            del self.lib
            self.lib = None
            print('D188 DLL unloaded successfully.')
        else:
            print('DLL not loaded. Nothing to unload.')

if __name__ == '__main__':
    print('Example script:')
    # Example usage
    Selector = D188Controller()
    Selector.Load()
    Selector.Initialize()
    time.sleep(0.1)
    Selector.SetMode('USB')
    time.sleep(0.1)
    Selector.SetIndicator('ON')
    time.sleep(0.1)
    Selector.SetDelay(1) # can go as short as 0.1ms, but now 1 for safety
    time.sleep(0.1)
    Selector.SetChannel(8)
    time.sleep(0.1)
    Selector.GetState()
    time.sleep(0.1)
    Selector.Close
    time.sleep(0.1)
    Selector.Unload()
