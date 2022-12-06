# microSWIFT - Version 1

[![Python Package using Conda](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/SASlabgroup/microSWIFT/actions/workflows/python-package-conda.yml)

<img src=./doc/images/microSWIFT.png alt="Artistic rendition of the microSWIFT wave buoy"  width="300">

Operational code for the microSWIFT v1 wave buoy developed at the University of Washington Applied Physics Laboratory (UW-APL).

Learn more about the microSWIFT wave buoy:

- https://apl.uw.edu/project/projects/swift/pdfs/microSWIFTspecsheet.pdf (spec sheet)

## Organization of the project

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
    │   │       ├── config_duty_cycle_not_int.txt
    │   │       ├── config_gps_freq_not_int.txt
    │   │       ├── config_gps_freq_out_of_range.txt
    │   │       ├── config_imu_freq_not_int.txt
    │   │       ├── config_imu_freq_out_of_range.txt
    │   │       ├── config_no_duty_cycle.txt
    │   │       ├── config_no_gps_freq.txt
    │   │       ├── config_no_imu_freq.txt
    │   │       ├── config_no_record_window.txt
    │   │       ├── config_record_window_not_int.txt
    │   │       ├── config_record_window_too_long.txt
    │   │       └── config_send_window_too_short.txt
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

## Data access: 
microSWIFT wave measurements in the form of spectral and bulk parameters are telemetered to the SWIFT server:
- http://faculty.washington.edu/jmt3rd/SWIFTdata/DynamicDataLinks.html (web page)
- https://swiftserver.apl.washington.edu/map/ (map)
- https://github.com/SASlabgroup/microSWIFTtelemetry (Python-based data access)

Raw data in the form of GPS and IMU time series is stored as `.dat` files in the onboard SD card in the `microSWIFT/data/` directory.
