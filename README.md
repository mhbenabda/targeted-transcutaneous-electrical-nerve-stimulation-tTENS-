# TTENS controll software for multielectrode psychophysics experiments

### About The Project
This project is a Python-based framework for conducting psychophysics experiments using the stimulation device [DS8R]([DS8R-url]) and the electrode selctor [D188]([D188-url]) from Digitimer. It allows for control of stimulation parameters (preset or dynamically), channel switching and automated data logging and plotting. The software integrates APIs for device communication and offers flexible workflows for  psychophysics experiments.

## Requirements
* __Operating System__: windows 7 or higher
* __Python version__: 3.11.9
* __PyQt version__: 5.15.9 (__Qt version__: 5.15.2)
* __DS8R DLL__: D128API.DLL 
* __D188 DLL__: DGD188API.DLL

__Note:__ Be carefull this code uses the original DLL and not the proxy DLL provided by Digitimer! Both DLLs are downloaded automatically with the windows app provided on each device webpage.


<!-- MARKDOWN LINKS & IMAGES -->
[DS8R-url]: https://www.digitimer.com/product/human-neurophysiology/peripheral-stimulators/ds8r-biphasic-constant-current-stimulator/
[D188-url]: https://www.digitimer.com/product/human-neurophysiology/stimulator-accessories/d188-remote-electrode-selector/d188-remote-electrode-selector/