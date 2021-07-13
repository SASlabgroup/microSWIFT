#!/bin/bash

# Description: Goal is to query the network to see which microSWIFTS are available then access each one of them 
# and use rsync to sync the data that is on the microSWIFT to a buffer on the local machine 
# INPUTS:
# lowest microSWIFT ID number
# highest microSWIFT ID number
# OUTPUT:
# transfers all data from each microSWIFT into a directory in the local machine in the main directory
# 

# User input on microSWIFT Range
read -p "Enter Lowest microSWIFT ID: " min
read -p "Enter Highest microSWIFT ID: " max
read -p "Enter UTC Date(DDMMMYYYY): " date
read -s -p "Enter Password: " password
printf "\n"

# Define date
DATESTRING=$date


# Define SWIFT Range
NUMSWIFTSMIN=$min
NUMSWIFTSMAX=$max

# Define microSWIFT IP address 
IP="192.168.0."
PASSWORD=$password

# Loop through each microSWIFT possible and see who is online
for MSNUM in $(seq $NUMSWIFTSMIN $NUMSWIFTSMAX)
do
    # Ping the microSWIFT
    # Note it must be two pings to send and receive otherwise it wont be reached
    ping -c 2  $IP$MSNUM 2>&1 >/dev/null; PINGVAL=$?
    # If microSWIFT is online, sync if not skip
    if [[ $PINGVAL -eq 0 ]]
    then
        echo "microSWIFT $MSNUM is online"
        # rsync locates data on microSWIFT and puts it in the local buffer
        # Potential Flags for rsync -avzh
        # To download on mac OS use the command: brew install hudochenkov/sshpass/sshpass
        sshpass -p $PASSWORD rsync -avzh --include=$DATESTRING pi@$IP$MSNUM:/home/pi/microSWIFT/data ./microSWIFT-data/$MSNUM
    else
        echo "microSWIFT $MSNUM is offline"
    fi
done







