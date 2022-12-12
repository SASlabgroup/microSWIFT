"""
The main operational script that runs on the microSWIFT V1 wave buoys.

This script sequences the microSWIFT data collection, post-processing,
and telemetering. Its core task is to schedule these events, ensuring
that the buoy is in the appropriate record or send window based on the
user-defined settings. The process flow is summarized as follows:

    1. Record GPS and record IMU concurrently; write to .dat files
    2. Read the raw data into memory and process it into a wave solution
    3. Create a payload and pack it into an .sbd message; telemeter the
       message to the SWIFT server.

Author(s):
EJ Rainville (UW-APL), Alex de Klerk (UW-APL), Jim Thomson (UW-APL),
Viviana Castillo (UW-APL), Jacob Davis (UW-APL)

microSWIFT is licensed under the MIT License.

"""

import concurrent.futures
import time
from datetime import datetime

import numpy as np

from .accoutrements import imu_module
from .accoutrements import gps_module
from .accoutrements import sbd
from .accoutrements import telemetry_stack
from .processing.gps_waves import gps_waves
from .processing.uvza_waves import uvza_waves
from .processing.collate_imu_and_gps import collate_imu_and_gps
from .utils import configuration
from .utils import log
from .utils import utils

def main():
    """
    Control flow for microSWIFT operations.
    """
    logger = log.init()
    config = configuration.Config('./config.txt')
    gps = gps_module.GPS(config)
    imu = imu_module.IMU(config)

    # Initialize the telemetry stack if it does not exist yet. This is a
    # text file that keeps track of the SBD message filenames that remain to
    # be sent to the SWIFT server. If messages are not sent during a send
    # window, the message filename will be pushed onto the stack and the
    # script will attempt to send them during the next window. This ensures
    # recent messages will be sent first.
    telemetry_stack.init()
    logger.info('Number of messages to send: %d', telemetry_stack.get_length())

    # `duty_cycle_count` keeps track of the number of duty cycles.
    duty_cycle_count = 1

    while True:
        recording_complete = False

        # If the current time is within any record window (between start
        # and end time) record the imu and gps data until the end of the
        # window. These tasks are submitted concurrently.
        if config.START_TIME <= datetime.utcnow() < config.END_RECORD_TIME:
            logger.info(log.header('Iteration %d', duty_cycle_count))
            record_window(gps, imu, config)
            recording_complete = True

        if recording_complete is True:
            payload = processing_window(gps, imu, logger, config)
            send_window(payload, logger, config)
            config.update_times() #TODO: remove and put after  else?
            duty_cycle_count += 1

        # The current time is not within the defined record window. Skip
        # telemetry and sleep until a window is entered. Log this
        # information at the specified interval (in seconds).
        else:
            config.update_times() #TODO: remove and put after  else?
            while datetime.utcnow() < config.START_TIME: #TODO: config.END_DUTY_CYCLE_TIME?
                time.sleep(10)
                logger.info('Waiting to enter record window')
        
        # config.update_times()
def record_window(gps, imu, config):
    """
    Schedule GPS and IMU recording.

    Parameters
    ----------
    gps : GPS class
    imu : IMU class
    config : Config class
    """
    # Records GPS and IMU data concurrently with
    # asynchronous futures. This is a two-step call that
    # requires scheduling the tasks then returning the result
    # from each Future instance. Flip the`recording_complete`
    # state when the tasks are completed.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        record_gps_future = executor.submit(gps.record,
                                            config.END_RECORD_TIME)
        record_imu_future = executor.submit(imu.record,
                                            config.END_RECORD_TIME)

        record_gps_future.result()
        record_imu_future.result()

    gps.power_off()
    imu.power_off()


def processing_window(gps, imu, logger, config):
    """
    Processes recorded data into a wave solution.

    Parameters
    ----------
    gps : GPS class
    imu : IMU class
    logger : Logger class
    config : Config class

    Returns
    -------
    dict
        Processed payload variables
    """
    # Process the data into a wave estimate based on the specified
    # processing type. Check that the appropriate modules are
    # initialized, otherwise log a warning and fill the all of the
    # results with bad values of the expected length.
    logger.info('Starting Processing')

    # GPS waves processing: convert the raw GPS data to East-West
    # velocity (u), North-South velocity (v), and elevation (z),
    # then produce a wave estimate.
    if config.WAVE_PROCESSING_TYPE == 'gps_waves' and gps.initialized:
        gps.to_uvz(gps.filename)
        payload = gps_waves(gps.u,
                            gps.v,
                            gps.z,
                            gps.fs)
        logger.info('gps_waves.py executed')

    # UVZA waves processing: convert the raw GPS data to East-West
    # velocity (u), North-South velocity (v), and elevation (z);
    # integrate the raw IMU to xyz displacements in the body or
    # earth frame; then collate these variables onto the same time
    # array and produce a wave estimate. The first two-minutes
    # are zeroed-out to remove filter ringing.
    elif config.WAVE_PROCESSING_TYPE == 'uvza_waves' \
                                    and gps.initialized \
                                    and imu.initialized:
        gps.to_uvz()
        imu.to_xyz()
        imu_collated, gps_collated = collate_imu_and_gps(imu, gps)

        zero_points = int(np.round(120*imu.fs))
        payload = uvza_waves(gps_collated['u'][zero_points:],
                             gps_collated['v'][zero_points:],
                             imu_collated['pz'][zero_points:],
                             imu_collated['az'][zero_points:],
                             imu.fs)
        logger.info('uvza_waves.py executed.')

    else:
        logger.info('A wave solution cannot be created; either the '
                    'specified processing type (=%s) is invalid, or '
                    'either or both of the sensors failed to initialize '
                    '(GPS initialized=%s, IMU initialized=%s). Entering '
                    'bad values for the wave products (=%d).',
                    config.WAVE_PROCESSING_TYPE, gps.initialized,
                    imu.initialized, config.BAD_VALUE)

        payload = utils.fill_bad_values(config)

    # check lengths of spectral quanities:
    if len(payload['E'])!=config.NUM_COEF \
                                    or len(payload['f'])!=config.NUM_COEF:
        logger.info('WARNING: the length of E or f does not match the '
                    'specified number of coefficients, %d; (len(E)=%d, '
                    'len(f)=%d).',
                    config.NUM_COEF, payload['E'], payload['f'])

    payload['u_mean'] = np.nanmean(gps.u)
    payload['v_mean'] = np.nanmean(gps.v)
    payload['z_mean'] = np.nanmean(gps.z)
    payload['last_lat'] = utils.get_last(config.BAD_VALUE, gps.lat)
    payload['last_lon'] = utils.get_last(config.BAD_VALUE, gps.lon)

    # Populate the voltage, temperature, salinity fields with place-
    # holders. These modules will be incorporated in the future.
    payload['voltage'] = 0
    payload['temperature'] = 0.0
    payload['salinity'] = 0.0

    return payload

def send_window(payload, logger, config):
    """
    Send payload to SWIFT server.

    Parameters
    ----------
    payload : dict
        Processed payload variables.
    logger : Logger class
    config : Config class
    """
    # Pack the payload data into a short burst data (SBD) message
    # to be telemetered to the SWIFT server. The SBD filenames are
    # entered into a stack (last in, first out) in the order in
    # which they were created such that the most recent messages
    # are sent first.
    logger.info('Creating TX file and packing payload data')
    tx_filename, payload_data = sbd.createTX(payload)

    # Push the newest SBD filenames onto the stack and return the
    # updated list of payload filenames. The list must be flipped
    # to be consistent with the LIFO ordering. Iterate through the
    # stack and send until the current time window is up. Update the
    # stack each loop (if a send is successful) and re-write the
    # payload filenames to the stack file.
    payload_filenames = telemetry_stack.push(tx_filename)
    payload_filenames_lifo = list(np.flip(payload_filenames))

    logger.info('Number of Messages to send: %d', len(payload_filenames))

    messages_sent = 0
    for tx_file in payload_filenames_lifo:
        if datetime.utcnow() < config.END_DUTY_CYCLE_TIME:
            logger.info('Opening TX file from payload list: %s', tx_file)

            with open(tx_file, mode='rb') as file:
                payload_data = file.read()

            successful_send = sbd.send(payload_data,
                                        config.END_DUTY_CYCLE_TIME)

            if successful_send is True:
                del payload_filenames[-1]
                messages_sent += 1
        else:
            # Exit if the send window has expired.
            break

    telemetry_stack.write(payload_filenames)

    # End of the loop; log the send statistics and increment the
    # counters for the next iteration.
    messages_remaining = len(payload_filenames) - messages_sent
    logger.info('Messages Sent: %d; Messages Remaining: %d',
                int(messages_sent), int(messages_remaining))

if __name__ == '__main__':
    main()
