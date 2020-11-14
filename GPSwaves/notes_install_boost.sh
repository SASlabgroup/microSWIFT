
#dpkg -S /usr/include/boost/version.hpp
#libboost1.58-dev:amd64: /usr/include/boost/version.hpp
#sudo xargs --null -a boost_1_69_0.tar apt-get install 
# copy tar file into /usr/local/src
sudo ./boostrap.sh
sudo .b2 install

