[![Python Package using Conda](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml)

# <img src= "./doc/images/SWIFTlogo.jpg" height="120" align=left></img>microSWIFT v1

Operational code for the microSWIFT v1 wave buoy developed at the University of Washington Applied Physics Laboratory (UW-APL).

## About microSWIFT

<img src=./doc/images/microSWIFT.png alt="Artistic rendition of the microSWIFT wave buoy"  width="300"  align=right></img>

MicroSWIFT is an expendable version of the [Surface Wave Instrument Float with Tracking](https://apl.uw.edu/project/project.php?id=swift) (SWIFT) platform. Original development of the microSWIFT buoy (now v1) began in 2020, led by engineers at the University of Washington Applied Physics Laboratory (UW-APL). It is built around a Raspberry Pi and runs operational code written in Python (this repository). This combination of developer-friendly hardware and easy-to-read code has fostered the creation of an effective tool for ocean wave research and student learning. This version of the microSWIFT continues to be developed and improved, and has been used to study breaking waves in nearshore environments, hurricanes, waves in sea ice, and more.

## Requirements

### Software requirements

The microSWIFT codebase is intended for operational use with unix-based operating systems, particularly the Raspbian GNU/Linux 10 (buster) distribution that runs onboard the microSWIFT's Raspberry Pi Zero, and with Python 3.7 (note this is not the preinstalled Python that ships with Raspbian). The code has been successfully run in the mock-based simulation mode intended for development and testing on macOS using python 3.7-3.9.

microSWIFT uses conda for package management. The required Python dependencies are specified in [environment.yml](https://github.com/SASlabgroup/microSWIFT/blob/main/environment.yml).

### Hardware requirements

MicroSWIFT v1 is built around a Raspberry Pi Zero with a 1GHz single-core CPU and 512MB RAM. Additional hardware requirements, notably the GPS, IMU, and Iridium modem, are specified in the [component specification](https://github.com/SASlabgroup/microSWIFT/blob/75-finish-design-doc/doc/component_specification).

## Installation

The latest release of microSWIFT can be installed from PyPI using pip:
```bash
pip install microSWIFT
```

## Usage

### Configuration
#TODO: e.g. config file use

### Data access

MicroSWIFT wave measurements in the form of spectral and bulk parameters are telemetered to the SWIFT server and are accessible using any of the following methods:

- [Web-based query](http://faculty.washington.edu/jmt3rd/SWIFTdata/DynamicDataLinks.html)
- [View a map of actively deployed SWIFTs](https://swiftserver.apl.washington.edu/map/)
- [microSWIFTtelemetry: Python-based data access](https://github.com/SASlabgroup/microSWIFTtelemetry)

Raw data in the form of GPS and IMU time series is stored on the onboard SD card in `.dat` format in the `microSWIFT/data/` directory.

### Repository Structure

```bash
microSWIFT/
├── LICENSE.md
├── README.md
├── doc
│   ├── component_specification
│   ├── functional_specification.md
│   ├── images/
│   └── microSWIFT_poster.pdf
├── environment.yml
├── examples
│   └── examples.ipynb
├── microSWIFT
│   ├── __init__.py
│   ├── accoutrements
│   │   ├── __init__.py
│   │   ├── adafruit_fxas21002c.py
│   │   ├── adafruit_fxos8700.py
│   │   ├── gps_module.py
│   │   ├── imu_module.py
│   │   ├── sbd.py
│   │   └── telemetry_stack.py
│   ├── checkout.py
│   ├── config.txt
│   ├── data/
│   ├── logs/
│   ├── microSWIFT.py
│   ├── mocks
│   │   ├── __init__.py
│   │   ├── mock_adafruit_fxas21002c.py
│   │   ├── mock_adafruit_fxos8700.py
│   │   ├── mock_board.py
│   │   ├── mock_busio.py
│   │   ├── mock_rpi_gpio.py
│   │   └── mock_serial.py
│   ├── processing
│   │   ├── __init__.py
│   │   ├── collate_imu_and_gps.py
│   │   ├── gps_waves.py
│   │   ├── integrate_imu.py
│   │   ├── transform_imu.py
│   │   └── uvza_waves.py
│   ├── tests/
│   ├── utils
│   │   ├── __init__.py
│   │   ├── configuration.py
│   │   ├── log.py
│   │   ├── microSWIFT.service
│   │   ├── pylint.txt
│   │   ├── setup.bash
│   │   ├── telemetry_stack.txt
│   │   └── utils.py
│   └── version.py
└── setup.py

```

### Contributions

#TODO: 
For consistency in results, contributors are encouraged to use conda for package management. 


### Acknowledgements
#TODO: