import ctypes
import os

class D128Controller:
    def __init__(self):
        self.PATH_PROXY = ''  # Set your path
        self.NAME_PROXY = 'D128RProxy.dll'
        self.ALIAS_PROXY = 'D128RProxy'

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

    def D128ctrl(self, command, *args):
        success = False
        if command.lower() == 'open':
            if len(args) == 0:
                success = self.Init()
                if success:
                    self.d128.update({'mode': 0, 'polarity': 0, 'source': 0, 
                                      'demand': 0, 'pulsewidth': 0, 
                                      'dwell': 0, 'recovery': 0, 'enabled': 0})
            else:
                print("Unexpected number of arguments for open command. It accepts no arguments.")

        elif command.lower() == 'close':
            if len(args) == 1:
                print('not implemented. useful to free resources') ### potential emprovement
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

    def Init(self):
        full_dll = os.path.join(self.PATH_PROXY, self.NAME_PROXY)

        try:
            self.lib = ctypes.CDLL(full_dll)
            return True
        except OSError:
            print(f"{full_dll} was not found!")
            return False

    def Close(self):
        # Implement the logic to close/unload the library if necessary
        return True

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


