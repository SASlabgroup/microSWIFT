# microSWIFT Design

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

## Hardware Components

### Raspberry Pi

At the heart of the microSWIFT is a Raspberry Pi Zero. This developer-friendly board, combined with easy-to-read Python-based code, makes the microSWIFT an effective tool for ocean wave research and student learning. An obvious tradeoff, however, is its high power consumption compared to that attainable with an embedded microcontroller and code.

### GPS

The GPS module is a GlobalTop FGPMMOPA6H provided on an Adafruit Ultimate GPS v3 breakout board. It provides the time, position, and velocity  datastreams to the microSWIFT. The last known position of the microSWIFT is reported to the server during every duty cycle as latitude and longitude in decimal degrees. The North and East doppler velocities are fundamental input to the onboard wave processing algorithms.

### IMU

The inertial measurement unit (IMU) is comprised of a 3-axis digital gyroscope (FXAS21002C) and a 6-axis integrated linear accelerometer and magnetometer (FXOS8700CQ), both provided on an Adafruit Precision NXP 9-DOF Breakout Board. The combined IMU measurements can be transformed, numerically integrated, and used to provide an alternative heave estimate in the wave processing.

### Iridium Modem
(TODO: description)

## Software Components
TODO: many of these can be adapted from the code comments/docstrss

### microSWIFT.py
(#TODO: description)

### Config class
(TODO: description of class, its methods, and attributes)

### GPS class
(TODO: description of class, its methods, and attributes)

### IMU class
(TODO: description of class, its methods, and attributes)

### Wave processing algorithms
(TODO: `gps_waves`, `uvza_waves` descriptions)

### SBD class
(TODO: description of class, its methods, and attributes)

### Telemetry stack
(TODO: description)

## Design Diagram

Process flow is controlled by `microSWIFT.py` module. At boot-up, `microSWIFT.py` is executed by `microSWIFT.service`. It then instantiates the `logger`, `Config`, `GPS`, and `IMU` objects and enters the record-process-send loop which runs indefinitely. Each loop is defined as one duty cycle. This is sequencing is summarized in the following flow chart:

```mermaid
flowchart LR
    start([start])--> initialization
    initialization --> in_record{"in record<br/>window?"};
    
    in_record-->|Yes| record_window["record<br/>window"]
        record_window-->recording_successful{"recording<br/>successful?"};
        recording_successful-->|Yes| processing_window["processing<br/>window"]
        processing_window-->send_window["send<br/>window"]
        send_window-->update_times
        recording_successful-->|No| wait

    in_record-->|No| wait["wait until the end<br/>of the duty cycle"]
        wait-->update_times["update current<br/>window times"]
    
    update_times-->in_record

    classDef blue fill:#a4ccf5,stroke:#000000,stroke-width:1px
    classDef green fill:#d4f5a4,stroke:#000000,stroke-width:1px
    classDef yellow fill:#f5f5a4,stroke:#000000,stroke-width:1px
    classDef orange fill:#f5d4a4,stroke:#000000,stroke-width:1px
    classDef darkgreen fill:#82b572,stroke:#000000,stroke-width:1px
    class initialization blue
    class record_window green
    class processing_window yellow
    class send_window orange
    class start darkgreen

```

### Initialization window

The initialization window is run once per boot. It instantiates  `logger`, `Config`, `GPS`, and `IMU` objects based on the user-defined configuration settings in `config.txt`. It also sets the defining window times, including the start of the duty cyle (= start of the `record window`), the end of the recording window, and the end of the duty cycle (note that the length of `send window` = a full duty cycle - `record window`).

```mermaid
flowchart LR
    user_config[/config.txt/]-->config["initialize config"];
    subgraph initialization["initialization window"]
        direction TB
        logger["initialize logger"]
        config-->gps["initialize GPS"] & imu["initialize IMU"] & set_time["set current window start and end times"];
    end

    classDef grey fill:#FFFFFF,stroke:#a3a0a0, stroke-width:1px
    classDef blue fill:#a4ccf5,stroke:#000000,stroke-width:1px

    class initialization,user_config grey
    class logger,config,gps,imu,set_time blue
```

### Record window

A record window is entered when the current time is between the start and end record window times, as determined by `Config`. Its main task is to power on the GPS and IMU, record them concurrently using `concurrent.futures`, and then power them down. The `record()` method of both `GPS` and `IMU` writes data to `.dat` files stored onboard.

```mermaid
flowchart TB
    subgraph record_window["record window"]
        direction TB
        gps_on["power on GPS"] --> imu_on["power on IMU"] --> futures
        subgraph futures["concurrent.futures"]
            direction TB
            record_gps["record GPS"]-->gps_data[(gps data)]
            record_imu["record IMU"]-->imu_data[(imu data)]
        end
        futures --> gps_off["power off GPS"] --> imu_off["power off IMU"] --> return([return])
    end

    classDef green fill:#d4f5a4,stroke:#000000,stroke-width:1px
    classDef grey fill:#FFFFFF,stroke:#a3a0a0, stroke-width:1px
    classDef red fill:#f7b2b2, stroke:#a3a0a0, stroke-width:1px

    class gps_on,imu_on,record_gps,record_imu,gps_data,imu_data,gps_off,imu_off green
    class record_window,futures grey
    class return, red

```

### Processing window

The processing window reads the previously recorded `.dat` files from the `GPS` and `IMU`  into memory, transforms the data into the appropriate coordinates, and produces a wave estimate based on the configured wave processing type. If the required data streams do not pass quality control, the payload is filled with bad values to be sent along with any remaining available data.

```mermaid
flowchart LR
    subgraph processing_window["processing window"]
    direction TB
    type{"processing type"} -->|"gps waves"| gps_good{"gps passes<br/>quality control?"}
        gps_good-->|yes| gps_to_uvz["transform (lat,lon) to (u,v)"]
            gps_to_uvz-->gps_waves[run gps_waves]
        gps_waves-->return
        gps_good-->|no| fill_bad_values["fill with bad values"]

    type{"processing type"} -->|"uvza waves"| gps_and_imu_good{"imu & gps pass<br/>quality control?"}
        gps_and_imu_good-->|no| fill_bad_values["fill with bad values"]

        gps_and_imu_good-->|yes| transform_imu_and_gps["transform (lat,lon) to (u,v) <br/> integrate imu to (x,y,z)"]
        transform_imu_and_gps-->uvza_waves["run_uvza_waves"]
        uvza_waves-->return


    fill_bad_values --> return([return])
    end

    classDef yellow fill:#f5f5a4,stroke:#000000,stroke-width:1px
    classDef grey fill:#FFFFFF,stroke:#a3a0a0, stroke-width:1px
    classDef red fill:#f7b2b2, stroke:#a3a0a0, stroke-width:1px
    
    class processing_window grey
    class type,gps_good,gps_and_imu_good,gps_to_uvz,gps_waves,fill_bad_values,transform_imu_and_gps,uvza_waves yellow
    class return, red

```

### Send window

In the send window, the payload is packed into a binary short burst data (`.sbd`) file and pushed onto a stack of messages to be sent. Until the duty cycle is up, or if the stack empties, messages are repeatedly read from the top of the stack and sent to the server. If a message fails to send, the loop continues to try to send it until the time expires.

```mermaid
flowchart LR
    subgraph send_window["send window"]
    direction LR
        pack["pack payload<br/>and push to<br/>telemetry stack"]-->in_send{"still in<br/>send window?"};
        in_send-->|yes| send["send from<br/>top of stack"];
            send-->send_successful{"send<br/>successful?"}
                send_successful-->|yes| update_stack["update<br/>stack"]
                    update_stack-->all_sent{"all messages<br/>sent?"}
                    all_sent-->|yes| return([return])

                    all_sent-->|no| in_send

                send_successful-->|no| in_send

        in_send-->|no| return
    end

    classDef orange fill:#f5d4a4,stroke:#000000,stroke-width:1px
    classDef grey fill:#FFFFFF,stroke:#a3a0a0, stroke-width:1px
    classDef red fill:#f7b2b2, stroke:#a3a0a0, stroke-width:1px
    class send_window grey
    class process,pack,in_send,send,update_stack,all_sent,send_successful orange
    class return red
```