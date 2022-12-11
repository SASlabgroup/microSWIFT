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

## Components

### Sensor Loggers
* Receive and store data for:
	* GPS
	* IMU

### Data store
* Data store for raw text data

### Data processor
* Functions to process raw text data

### Sensor Testers
* Functions to fully test functionality of sensors and sensor loggers

### Transmission Unit Tester
* Functions to test functionality of transmission unit

### Configuration UI
* Functions to ingest user set configurations for sensor and transmission functionality


## Design Diagram 
This is an example of using the mermaid diagram tool 

```mermaid
flowchart TD;
    start([start])-->logger["init_logger"] & config["init_config"];
    user_config[/config.txt/]-->config
    config-->gps["init GPS"] & imu["init IMU"] & set_time["set current window start and end times"];
    set_time-->in_record{"in record window?"};

    in_record-->|Yes| record_gps["record IMU and GPS"] & record_imu["record IMU"]
        record_gps & record_imu-->recording_successful{"recording successful?"};
        recording_successful-->|Yes| process["process data"]
            process-->pack["pack payload and push to telemetry stack"]
            pack-->in_send{"in a send window?"}
            in_send-->|yes| send["send from top of stack"];
                send-->send_successful{"send successful?"}
                    send_successful-->|yes| update_stack["update stack"]
                        update_stack-->all_sent{"all messages sent?"}
                        all_sent-->|yes| wait

                        all_sent-->|no| in_send

                    send_successful-->|no| in_send

            in_send-->|no| wait

        recording_successful-->|No| wait

    in_record-->|No| wait["wait until the end of the duty cycle"]
    wait-->update_times["update current window times"]    
    update_times-->in_record

```

```mermaid
flowchart TB
    start([start])--> initialization

    subgraph initialization
        direction TB
        logger["init_logger"]
        user_config[/config.txt/]-->config["init_config"];
        config-->gps["init GPS"] & imu["init IMU"] & set_time["set current window start and end times"];
    end

    subgraph record_window
        direction TB
        record_gps["record IMU and GPS"]
        record_imu["record IMU"]
    end

    initialization-->in_record{"in record window?"};
    in_record-->|Yes| record_window

    in_record-->|No| wait["wait until the end of the duty cycle"]
    wait-->update_times["update current window times"]    
    update_times-->in_record

```
---

Main process flow controlled by `microSWIFT.py`:
```mermaid
flowchart LR

    start([start])--> initialization
    initialization --> in_record{"in record window?"};
    
    in_record-->|Yes| record_window["enter record window"]
        record_window-->recording_successful{"recording successful?"};
        recording_successful-->|Yes| send_window["enter send window"]
        send_window-->update_times
        recording_successful-->|No| wait

    in_record-->|No| wait["wait until the end of the duty cycle"]
        wait-->update_times["update current window times"]
    
    update_times-->in_record

```

Details of the initialization:
```mermaid
flowchart LR
    user_config[/config.txt/]-->config["init_config"];
    subgraph initialization
        direction TB
        logger["init_logger"]
        config-->gps["init GPS"] & imu["init IMU"] & set_time["set current window start and end times"];
    end
```

Record window:
```mermaid
flowchart TB
    subgraph record_window
        direction TB
        gps_on["power on GPS"] --> imu_on["power on IMU"] --> futures
        subgraph futures["concurrent.futures"]
            direction TB
            record_gps["record GPS"]-->gps_data[(gps data)]
            record_imu["record IMU"]-->imu_data[(imu data)]
        end
        futures --> gps_off["power off GPS"] --> imu_off["power off IMU"]
    end
```
