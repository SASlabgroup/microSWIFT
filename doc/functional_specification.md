# Functional Specification

## Background

MicroSWIFT is an expendable version of the [Surface Wave Instrument Float with Tracking](https://apl.uw.edu/project/project.php?id=swift) (SWIFT) platform. The small, low-cost instruments measure waves at the ocean surface and telemeter their data back home via satellite. Original development of the microSWIFT buoy (now v1) began in 2020, led by engineers at the University of Washington Applied Physics Laboratory (UW-APL). It is built around a Raspberry Pi and runs operational code written in Python (this repository). This combination of developer-friendly hardware and easy-to-read code has fostered the creation of an effective tool for ocean wave research and student learning. This version of the microSWIFT continues to be developed and improved, and has been used to study breaking waves in nearshore environments, hurricanes, waves in sea ice, and more.

Please visit the following links to learn more about the microSWIFT and its applications:

- Video on the use of microSWIFTs for coastal wave measurements - [microSWIFTs: Tiny Oceanographic Floats Measure Extreme Coastal Conditions
](https://www.youtube.com/watch?v=rf76fkpzcrg) [youtube.com]
- Project page on the use of air-deployed microSWIFTs for [hurricane coastal impact forecast improvements](https://nopphurricane.sofarocean.com/team/thomson) [nopphurricane.sofarocean.com]

## Users and Use Cases

### Researchers

*Goal*: to easily configure microSWIFTs and deploy them in the field.

A researcher would like to be able to quickly and easily configure a microSWIFT to prepare it for data collection. The researcher also would like to have a high degree of confidence that all of the sensors are working correctly before deployment. The researcher has a high level of domain expertise but likely only a medium-level of technical competency.

*Use Cases:*

- Configure an existing buoy
- Confirm the hardware and software are working as expected
- Deploy and recover a buoy in the field

### Technicians

*Goal:* to build and configure microSWIFTs.

Technicians assemble and perform the initial configuration of the microSWIFTs, often in large quantities. The technician needs to be able to know whether or not the sensors have been connected correctly and receive detailed diagnostic information if they are not. The technician has a high technical competency (on both the hardware and software side) but may not be a domain expert.

*Use Cases:*

- Individual sensor testing
- Full system diagnostics
- Fully configure system

### Developers

*Goal:* to add software or hardware features to the microSWIFT.

A developer should be able to make modifications to the microSWIFT operational software or hardware with confidence that their additions will work in harmony with the remaining components. This requires well-designed unittests that achieve a high level of code coverage, as well as the ability to run the codebase on a personal machine (i.e. without the hardware on hand). Through repo- and code-level documentation, the developer should know how to contribute to the microSWIFT repository, including the required software dependencies as well as the maintaining group's integration workflow and code review procedures.

*Use Cases:*

- Clone or fork the repo and install the required dependencies in a conda environment on their personal machine
- Run the existing unit tests and know where to add new ones
- Add to (or modify) the existing repository on GitHub using pull requests
- Submit bug reports through GitHub issues
