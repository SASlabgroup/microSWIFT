# UVic's modified microSWIFT buoy

UVic had slightly different requirements for the microSWIFT buoy, which resulted
in a slightly modified design and software. UVic's version is operated close
to the beach/shore and is measuring the local currents and waves close to shore.

## Modifications in Autumn 2024:
- Johannes came back from a conference where participants stated that 12.5 Hz
  data taking frequency of the IMU is by far not enough. So, we looked at what's
  possible with the current (or slightly modified) hardware and software setup.

### Increase Clock Frequency on I2C bus
Even with pure python code, we quickly ran into limitation of the default 100kHz bus
frequency, so we needed to increase it by modifying one line in `/boot/config.txt`
on the raspberry pi:
```
dtparam=i2c_arm_baudrate=400000
```
Note, that there are reports that a value of 1000000, i.e. 1MHz, is also possible.
This might be required if we need to go to higher rates than we are aiming at,
namely readout rates of 833Hz or even higher. We have not tested this yet.

### Max Frequency from pure Python
A quick python test program allowed us to read out the IMU only at 250 Hz, although
the IMU was configured to deliver at 1.66kHz. So, lots of samples were dropped.
Lower configured rates had a lower number of dropped measurements, but they were
still clearly visible.

### move to C++ Code for reading out IMU
The modular code allowed for a simple adaption such that the IMU was read out by
c++, but the rest of the code for reading out GPS was unaltered.
[minimu9-ahrs](https://github.com/DavidEGrayson/minimu9-ahrs) from Pololu allows
reading out the IMU from c++ and worked out of the box. The overall CPU consumption
with the c++ code also dropped significantly.

We applied small modifications to adopt it to our needs (same units for printout,
fixed sample size, writing to a file in a certain format, etc.). We are including
the new code in this repository. Note that we removed the requirement of having
the eigen library installed, as we don't need that.
With the same, old hardware configuration we are now archiving reliably higher
readout rates with lower dropped measurements. The original code in our
configuraton uses 20minute readout windows, so the short c++ test emulated that:

| set  to [Hz]    |   nominal samples in 20 mins |  actually read out samples in 20 mins | dropped samples [%] |
| -- | -- | -- | -- |
| 12.5            | 14400                        |   14400      |   0   |
| 26              | 31200                        |    30747      |  1.45 |
| 52              | 62400                        |    61500      |  1.44 |
| 104             | 124800                       |    122914      |  1.51 |
| 208             | 249600                       |    245048      |  1.82 |
| 416             | 499200                       |    454551      |  8.94 | 
| 833             | 999600                       |    706466      | 29.33 |

The IMU chip can go higher, but needs a different mode to read it out. We stopped at 833Hz,
because we are loosing already 30% of the samples. At first sight, the CPU consumption
at 833 Hz was similar to the python only at 12.5Hz, at lower rates it drops significantly
(c++ code alone used 23% @ 833Hz, 15% @ 416 Hz, about 10% at 26-200Hz and  8% at 12 Hz).
At this point, as the CPU consumption was so low and we still miss samples, we thought
there's a contention that the single CPU core is busy when new samples should be read out.
The Raspberry Pi Zero 2 W has the same layout, is pin compatible, uses a similar amount
of power, but has a more modern 4 core CPU. We decided to try out replacing the CPU.

### new Raspberry Pi Zero 2 W
With the new exchanged CPU the readout rate across all intermediate rates is now consistently
1.35% lower than what's configured. This now seems to be a feature of the chip, because
if we now plot the time difference between samples being read out, a very sharp peak
appears. For the single CPU this plot was much more smeared out, so it appears we are
not loosing 1.35% of the samples, the IMU delivers samples at a 1.35% lower rate than
configured. At 833Hz configured rate we actually see 696.8 samples per second with
the plot of time difference very smeared out. Here we are running into a congestion on
the I2C bus, and a higher bus frequency would be required to run at 833Hz.

The difference in actual and configured output data rate (ORD) can be read out from the
chip, as described in chapter 6.4 of applicaton note AN5272 from https://www.st.com,
via reading out the INTERNAL_FREQ_FINE register and applying the formula in the
application note. The application note is also in the docs folder in this repo.
Note, that this register can only be read out, not set. The value of this register
will be printed after each 20 minute data taking block into the logfile on the buoy.

### new Configuration Options
New options for configuring the IMU are now listed in utils/Config.dat under the
IMU section.
Note that with the new c++ options, a lot of the new options are now hardcoded in c++,
soonly in `imuRate` is configurable at the moment. Possible values are listed in
`Config.dat` and range in several steps from 1.6 Hz to 6.6kHz, but in current
configuration only readout rates up to 416Hz are recommended. Higher rates at least
need a higher I2C clock and / or a FIFO mode with interrupts for readout. Also note,
that the chip allows for internal timestamps that can read out with the data,
this might be required for faster readouts than at 416 Hz.

#### Modified Instructions to Update / Install New Code
If you install from scratch, then run commands 1.-17. before
17a. After checking out the UVic branch, compile the c++ code
     ```
     sudo apt-get install libboost-program-options-dev libeigen3-dev
     ( cd cpp/minimu9-ahrs/; make )
     ```

## Two main Modifications in early 2024 were:
- transmission of location and data back to a station at nearby shore via radio
  instead of Iridium satellite transmision
- continuous data taking and continous transmission of location back to shore

### Radio Transmision of Location and Wave Parameters
The radio was to allow a live transmission of buoy locations to the station
at the shore, but alos to avoid an expensive subscription to the Iridium
service. After some testing we decided to use this radio
[RDF900ux](https://store.rfdesign.com.au/rfd-900ux-us-fcc-approved-hs-8517-62-00-90/) from [RFDesign](https://rfdesign.com.au).

It is commonly used in FPV drone application for transmitting telemetry data
back to the pilot on ground.

We changed to multi-point firmware with the beach station as radio with the
nodeID of 1, making it the master. We created buoys 2-12, where the buoy number
also reflects the nodeID of the radio in buoy2-12. The nodeIDs were hardcoded
in the firmware and updated while uploading the multipoint firmware. All other
parameters were then changed during runtime, see the corresponding python
scripts in the repo.

The radios are connected via inexpensive FTDI cables and are connected
to the USB port on the Raspberry Pi Zero. See [pictures] for more details.
More details about the hardware can be found in the hardware folder in the
repository (to be filled in spring '24).

Contact us if you want to find out more about the radio or for more details.

### Continous data taking and continous transmission of location
In order to be able to find the drifting buoys at the beach we needed to
continuously transmit the current location of the buoy back to the shore and,
ideally, in the case of loosing one buoys, transmit also the wave data
back to shore. Continous data taking was archieved by a special set of
parameters for the data taking, while leaving much of the code unchanged.
We are now taking data every 20 minutes for 17 minutes. This leaves 3 minutes
to calculate the wave data and transmit it back to shore. Then, another
20 minute window starts. During the 17 minute data taking, the current GPS
location is transmitted back to shore and displayed in near real time.
While it is maybe possible to shrink the transmission window from 3 minutes
down to 2 or 1 minute, no attempts have been done to further test this.
For our application, the 3 minute break is acceptable.


# Installation instructions for UVic's modified microSWIFT buoy
The OS on the Raspberry Pi Zeros were based on the Debian Bookworm release,
requiring some modifications of the installation instructions.
Below, you'll find the full installation instructions for the
software on the buoys as well as the required software on the beach station,
which ideally runs a debian based linux flavour, possibly in a VM.

We used 32GB SD cards for the OS and for storing the data. This should
allow for storing of weeks of data. Note, that every 20 minute interval
several files will be writting. So, over time a lot of data files will be
created. We strongly recommend to move old data files into subdirectories,
if not remove them altogether.

Here are the required steps to install all necessary software on the buoys.

1. Copy the OS image to the SD card, check for instructions e.g. here
   [Raspberry Pi Org](https://www.raspberrypi.com/documentation/computers/getting-started.html#install-an-operating-system)
   Note, that depending on the instructions some steps below can be omitted.

2. Enable ssh and create an user "microswift" on the image. This seems now
   trivial with the official imager, but if you use other methods to write
   the OS to the SD, you might need to:
   - With the SD image still in the computer that wrote the OS to the SD card,
     create an empty file named "ssh" on the boot partition of the SD card.
   - If working, create a "userconf.txt" on the same partition, however
     this step didn't work for us.
   - configure the wireless by creating a file "wpa_supplicant.conf" on
     the boot partition
        ~~~
        cat << EOF > <bootfs>/wpa_supplicant.conf
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        country=CA
        update_config=1
        
        network={
         ssid="muswift"
         psk="<passwotk for myswift>"
        }
        EOF
        ~~~
   - add your ssh key to the root user on the OS, so that you can login:
        ```
        mkdir <rootfs>/root/.ssh
        chmod 700 <rootfs>/root/.ssh
        echo "<ssh-key>" > <rootfs>/root/.ssh/authorized_keys
        chmod 600 /media/seuster/rootfs/root/.ssh/authorized_keys
        ```
   - give the buoy its correct name, e.g. "buoy2"
        ```
        echo "buoy2" > <rootfs>etc/hostname
        ```
     and change the name in <rootfs>/etc/hosts from raspberry to "buoy2"
   - enable uart, RTC and disable bluetooth in <bootfs>/config.txt by
     adding those lines at the bottom
        ```
        enable_uart=1
        dtoverlay=i2c-rtc,pcf8523
        dtoverlay=disable-bt
        ```
3. now it's time to insert the SD card into the Raspberry Pi Zero and boot
   for the first time !
4. Once booted, and when you're on the same wireless network as the buoy,
   ssh into the buoy as the root user with the ssh-key installed earlier.
5. pre-emptive, fix permissions for the microsoft user with these commands:
    ```
    usermod -aG dialout microswift
    ```
   you might need to create this user first, depending on the first step.
   and install ssh-keys for this user. We decided to just copy over the
   existing ssh-keys for the root user. NOTE: it's also a good practive to
   change the port for the ssh connection, during our development phase,
   the Raspberry Pi Zero was sometimes readily available on the world wide web!
6. Since we'll be using the RTC, disable the fake-hardware clock by following
   [this](https://pimylifeup.com/raspberry-pi-rtc/) recipe
    ```
    nano /lib/udev/hwclock-set
    ```
7. enable i2c, spi and uart in raspi-config
8. if not done already, also enable wireless in raspi-config
   NOTE: if wireless isn't working for you, you can still ssh into the
   computer via the USB connection ! Do an internet serach for
   "raspberry pi login via USB" or similar
9. You might want to set the timezone for your computer
    ```
    echo "TZ='America/Vancouver'; export TZ" >> /home/microswift/.profile
    ```
10. as a final step before rebooting install possible updates for the OS
    ```
    apt-get update
    apt-get upgrade --with-new-pkgs
    ```
    and install some required packages - some just for convenience
    during software development:
    ```
    apt-get -y install lsof git pylint supervisor xterm ntpdate 
    apt-get -y install python3-virtualenv libatlas3-base i2c-tools
    ```
11. the various changes in raspi-config and config.txt of the boot partition
    now finally require a reboot.
12. login as the microswift user
13. create virtualenv for python:
    ```
    mkdir -p microswift; cd microswift; virtualenv .
    ```
14. and activate it
    ```
    . bin/activate
    ```
15. install required python packages in the virtualenv
    ```
    pip3 install pynmea2 numpy Adafruit-Blinka adafruit-circuitpython-lis3mdl \
       adafruit-circuitpython-lsm6ds adafruit-circuitpython-ina219
    ```
16. Some of the originl sw still remembers the previous location of the
    software, so to avoid any rare pitfalls, fix the paths:
    ```
    (cd /home; sudo ln -s microswift/microswift pi)
    ```
17. Install the software from github and change to the "UVic" branch
    ```
    git clone https://github.com/SASlabgroup/microSWIFT
    cd microSWIFT
    git checkout UVic
    ```
18. run it for testing:
    ```
    python3 test_microSWIFT.py
    ```

19. set up to run it automatically (should be installed in a previous step):
    ```
    sudo apt-get -y install supervisor
    ```
20. install run.sh
21. copy over microswift.conf and enable & start the supervisor service
    ```
    sudo mv microswift.conf /etc/supervisor/conf.d/
    sudo systemctl enable supervisor
    sudo systemctl start supervisor
    ```


With the next reboot the software should start via the supervisord service
automatically. If not, check files in the /var/log/supervisor directory for
warnings or errors. Also, in /home/microswift/microswift/microSWIFT/logs
are mptest.log files that might show what's going wrong.

# Software installation on the laptop for the beach station
The following recipe is for debian based, modern system. We tested on
Debian bookworm and Ubuntu 22.03, with grafics.

1. create a microswift user
    ```
     adduser microswift
    ```
2. install system wide some required python packages
    ```
    apt-get install python3-serial-asyncio
    ```
3. login as the user micoswift and open a terminal
    ```
    mkdir measurement
    cd measurement
    wget https://seuster.web.cern.ch/seuster/MS/receive_radio3.py
    wget https://seuster.web.cern.ch/seuster/MS/display.py
    ```
4. as the root user, or via sudo download & install gpxsee.
   the xdotool might or might not allow you to automatically reload the
   maps with the current location of the buoys once new locations arrive
   at the station. You might need to change the key for the automated
   reload, it might just not work at all.
    ```
    wget "https://download.opensuse.org/repositories/home:/tumic:/GPXSee/Debian_Testing/amd64/gpxsee_13.4-1_amd64.deb"
    dpkg -i gpxsee_13.4-1_amd64.deb
    apt-get install xdotool
    ```
