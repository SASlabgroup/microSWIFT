#
g++ -c -fPIC -c *.cpp  -ggdb -I/usr/include/python3.7 -L/usr/lib/python3.7 -I/usr/local/include/boost -L/usr/local/lib/boost -I/usr/local/include/boost/python -L/usr/local/lib/boost/python 

g++ -fPIC -shared -Wl,-soname,processIMU_lib.so -ggdb -o processIMU_lib.so  -Wno-undef -I/home/kay/Desktop/microswift/microSWIFT/IMUprocessing *.o -I/usr/include/x86_64-linux-gnu -L/usr/lib/x86_64-linux-gnu -lm -g -I/usr/local/include/boost  -L/usr/local/lib/boost  -I/usr/include/python3.7 -I/usr/local/include/boost/python -L/usr/local/lib/boost/python -L/usr/local/lib/boost_python37 -L/usr/local/lib/boost_numpy37 -L/usr/lib/python3.7 -lpython3.7m -lboost_python37 -lboost_numpy37


#g++ -c -fPIC hello.cpp -o hello.o
#g++ -shared -Wl,-soname,hello.so -o hello.so  hello.o -lpython3.7 -lboost_python



