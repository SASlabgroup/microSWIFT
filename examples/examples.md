# Using the microSWIFT wave bouy
This notebook gives a quick tutorial on how to setup and operate a microSWIFT
wave bouy. This tutorial will not show how to build the hardware, for that see 
the docs directory.

## Setting up the software on a microSWIFT
Set up the raspberry pi and ssh into it using the following commands:

ssh pi@192.168.0.PI_NUMBER

password: PASSWORD

From here you will be at the root directory (~) on the microSWIFT. Now 
install the software to the root directory using the command: 

pip3 install --target-. microSWIFT

This command installs the microSWIFT software in the root directory. From here,
the user will need to move a service script(which allows the main microSWIFT.py
script to run as soon as the rapsberry pi is booted up) into the service directory
with the following commands:

cd microSWIFT/microSWIFT/utils/
mv ./microSWIFT.service /lib/systemd/system

Now that the service script is moved to the correct location, you need to
activate the service script with the following command: 

systemctl enable microSWIFT.service
systemctl start microSWIFT.service

These commands will now make it so the main microSWIFT.py script runs
when the bouy is booted up.

## Viewing the log file in realtime
To view the log file as the instrument records, use the following command:

From root directory: 

cd microSWIFT/microSWIFT/logs/
tail -f microSWIFT.log

