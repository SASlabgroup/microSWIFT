[![Python Package using Conda](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml)

# <img src= "./doc/images/SWIFTlogo.jpg" height="120" align=left></img>microSWIFT v1

<img src=./doc/images/microSWIFT.png alt="Artistic rendition of the microSWIFT wave buoy"  width="300"  align=right></img>

Operational code for the microSWIFT v1 wave buoy developed at the University of Washington Applied Physics Laboratory (UW-APL).

## About microSWIFT
The microSWIFT is an expendable version of the SWIFT platform, blah blah... 

Learn more about the microSWIFT wave buoy:

- https://apl.uw.edu/project/projects/swift/pdfs/microSWIFTspecsheet.pdf (spec sheet)

Publications!

## Requirements
(e.g. need a raspberry pi microSWIFT...!)
Hardware
Python version

## Installation
How to load onto a raspberry pi

## Usage
### Configuration
e.g. config file use

### Data access: 
microSWIFT wave measurements in the form of spectral and bulk parameters are telemetered to the SWIFT server:
- http://faculty.washington.edu/jmt3rd/SWIFTdata/DynamicDataLinks.html (web page)
- https://swiftserver.apl.washington.edu/map/ (map)
- https://github.com/SASlabgroup/microSWIFTtelemetry (Python-based data access)

Raw data in the form of GPS and IMU time series is stored as `.dat` files in the onboard SD card in the `microSWIFT/data/` directory.



### Repository Structure

```
microSWIFT/
├── LICENSE
├── README.md
├── doc
│   ├── Design.md
│   └── images
│       └── microSWIFT.png
├── environment.yml
├── examples
│   └── examples.ipynb
└── microSWIFT
    ├── __init__.py
    ├── accoutrements
    │   ├── __init__.py
    │   ├── adafruit_fxas21002c.py
    │   ├── adafruit_fxos8700.py
    │   ├── gps.py
    │   ├── imu.py
    │   ├── imu_checkout.py
    │   ├── sbd.py
    │   └── telemetry_stack.py
    ├── checkout.py
    ├── config.txt
    ├── microSWIFT.py
    ├── processing
    │   ├── __init__.py
    │   ├── collate_imu_and_gps.py
    │   ├── gps_waves.py
    │   ├── integrate_imu.py
    │   ├── transform_imu.py
    │   └── uvza_waves.py
    ├── tests
    │   ├── __init__.py
    │   ├── test_checkout.py
    │   ├── test_configuration.py
    │   ├── test_data
    │   │   └── config_files
    │   ├── test_imu_checkout.py
    │   └── test_microSWIFT.py
    └── utils
        ├── __init__.py
        ├── configuration.py
        ├── log.py
        ├── microSWIFT.service
        ├── pylint.txt
        ├── setup.bash
        └── utils.py
```

### Contributions

### Acknowledgements
