#!/bin/bash
# Run record and send gps python file for microSWIFT 

#directories and files needed 
GPSwavesDir=/home/pi/microSWIFT/testmicroWave/GPSwaves
config=/home/pi/microSWIFT/testmicroWave/config/Config.dat
configDir=/home/pi/microSWIFT/testmicroWave/config/
lib=/usr/local/lib/python2.7/dist-packages

#get PIDs  
gpsPID=$(ps -ef | grep "logGPS.py" | grep -v grep | awk '{ print $2 }')
echo "logGPSPID=" $logGPSPID

#add directories needed to run temp,pressure,humidity app to pythonpath
export PYTHONPATH=$PYTHONPATH/$GPSwavesDir:/$configDir

#=================================================================================
#killl apps if necessary 
#=================================================================================
if [ $# -eq 1 ]; then
    if [ $1 == "stop" ]; then
        echo "STOP Requested"
        # Kill the control GUI if it's running
        if [ ! -z $logGPSPID ]; then
            echo "Killing mswift app"
            sudo kill -9 $logGPSPID
        else
            echo "logGPS not running"
        fi 
        exit 
    fi 
fi 

#=================================================================================
#Kill running apps 
#=================================================================================
./runlogGPS stop 

#=================================================================================
#Run app
#=================================================================================
echo " --- RUN RECORD AND SEND GPS APP ---"
python2 logGPS.py $config &