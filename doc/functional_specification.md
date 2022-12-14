# Functional Specification

## Background

MicroSWIFT is an expendable version of the [Surface Wave Instrument Float with Tracking](https://apl.uw.edu/project/project.php?id=swift) (SWIFT) platform. Original development of the microSWIFT buoy (now v1) began in 2020, led by engineers at the University of Washington Applied Physics Laboratory (UW-APL). It is built around a Raspberry Pi and runs operational code written in Python (this repository). This combination of developer-friendly hardware and easy-to-read code has fostered the creation of an effective tool for ocean wave research and student learning. This version of the microSWIFT continues to be developed and improved, and has been used to study breaking waves in nearshore environments, hurricanes, waves in sea ice, and more.

Please visit the following links to learn more about the microSWIFT and its applications:

- Video on the use of microSWIFTs for coastal wave measurements - [microSWIFTs: Tiny Oceanographic Floats Measure Extreme Coastal Conditions
](https://www.youtube.com/watch?v=rf76fkpzcrg) [youtube.com]
- Project page on the use of air-deployed microSWIFTs for [hurricane coastal impact forecast improvements](https://nopphurricane.sofarocean.com/team/thomson) [nopphurricane.sofarocean.com]

## Users and Use Cases

### Researchers: Want to deploy the microSWIFT and change settings

A researcher would like to be able to quickly and easily install the microSWIFT software on a buoy with the appropriate hardware so that they may collect data. The researcher also would like to have a high degree of confidence that all of the sensors are working correctly before deployment. Finally, the researcher would like an easy way to configure setting regarding data collection and data transmission. The researcher has a high level of domain expertice but likely only a medium-level of technical competency.

Use Cases:

* Install microSWIFT software on newly built buoy
* Run diagnostic test on sensors and transmission unit
* Based on diagnostic tests, know if a sensor is working or not
* Configure sensor and transmission settings

### Technicians: Wants to build the microSWIFT

The technician is the user who actually built the physical buoy. The technician needs to be able to know whether or not the sensors have been installed correctly and receive detailed diagnostic information if they are not. The technician has a high technical competency (on both the hardware and software side) but wouldn't necessarily be a domain expert.

* Individual sensor testing
* Full system diagnostics
* Fully configure system

### Developers: Wants to add features to the microSWIFT (software and hardware)

Able to read documentation and add features.
