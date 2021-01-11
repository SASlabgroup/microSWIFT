# old directions
#dpkg -S /usr/include/boost/version.hpp
#libboost1.58-dev:amd64: /usr/include/boost/version.hpp
#sudo xargs --null -a boost_1_75_0.tar apt-get install 

# instructions for python 3.7
# download file from https://www.boost.org/users/download/
# or use the copy in microSWIFT/GPSwaves/boost_1_75_0
# copy tar file into /usr/local/src
sudo apt-get install python3-dev
sudo cp boost_1_75_0.tar.gz /usr/local/src/.
sudo tar xzvf boost_1_75_0.gz
sudo rm boost_1_75_0.tar.gz
cd boost_1_75_0
sudo ./bootstrap.sh --with-python-version=3.7
sudo ./b2 install 

