# UVic's modified microSWIFT buoy

UVic had slightly different requirements for the microSWIFT buoy, which resulted
in a slightly modified design and software. UVic's version is operated close
to the beach/shore and is measuring the local currents and waves close to shore.

Two main modifications were:
- transmission of location and data back to a station at nearby shore via radio
  instead of Iridium satellite transmision
- continuous data taking and continous transmission of location back to shore

### Radio Transmision of location and wave parameters
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
