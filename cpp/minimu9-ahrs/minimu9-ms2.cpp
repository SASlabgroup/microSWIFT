#include "version.h"
#include "prog_options.h"
#include "minimu9.h"
#include "exceptions.h"
#include "pacer.h"
#include <iostream>
#include <iomanip>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <pthread.h>
#include <system_error>
#include <chrono>
#include <fstream>
#include <string>
#include <stdio.h>
#include <time.h>

// TODO: print warning if accelerometer magnitude is not close to 1 when starting up

void stream_raw_values(imu & imu, long samples, uint16_t f, std::ofstream& of)
{
  // printf("going to stream raw samples %ld\n", samples);
  long now(0);
  timeval startTime;
  gettimeofday(&startTime,NULL);
  imu.enable(f);
  // 1 s = 1e6 mu sec, take 65% of that
  long wait = 650000;
  float elapsed(0.0);
  switch (f)
    {
    case 0b1000:
      wait/=1666;
      elapsed=samples / 1666;
      break;
    case 0b0111:
      wait/=833*1.25;
      elapsed=samples / 833;
      break;
    case 0b0110:
      wait/=416*1.1;
      elapsed=samples / 416;
      break;
    case 0b0101:
      wait/=208;
      elapsed=samples / 208;
      break;
    case 0b0100:
      wait/=104;
      elapsed=samples / 104;
      break;
    case 0b0011:
      wait/=52;
      elapsed=samples / 52;
      break;
    case 0b0010:
      wait/=26;
      elapsed=samples / 26;
      break;
    case 0b0001:
      wait/=12;
      elapsed=samples / 12;
      break;
    };
  // chip scale for this accel range + nominal g on earth
  //  this value is for +- 8G range, which is currently hard coded
  const float as=0.000244 * 9.80665;
  const float gs=0.07 * 3.14159265 / 180;
  
  char buffer[128];
  
  bool take_data(true);
  while( now++ < samples && take_data )
  {
    imu.read_raw();
    timeval curTime;
    gettimeofday(&curTime, NULL);

    take_data = curTime.tv_sec-startTime.tv_sec < elapsed;
    
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %X", std::gmtime(&curTime.tv_sec));
    of << buffer << "."
       << std::setfill('0') << std::setw(6) << curTime.tv_usec << ","
       << as*float(imu.a[0]) << "," << as*float(imu.a[1]) << "," << as*float(imu.a[2]) << ","
       << imu.m[0] << "," << imu.m[1] << "," << imu.m[2] << ","
       << gs*float(imu.g[0]) << "," << gs*float(imu.g[1]) << "," << gs*float(imu.g[2]) << "\n";

    // sleep between samples, another usleep waiting for new data
    // maybe 65% of 1/f
    usleep(wait);
  }
}

int main_with_exceptions(int argc, char **argv)
{
  prog_options options = get_prog_options(argc, argv);
  
  //  std::cout << "options: " << options.samples << "\n";
  
  if (options.show_help)
  {
    print_command_line_options_desc();
    std::cout << "For more information, run: man minimu9-ahrs" << std::endl;
    return 0;
  }

  if (options.show_version)
  {
    std::cout << VERSION << std::endl;
    return 0;
  }

  // Decide what sensors we want to use.
  sensor_set set;
  set.mag = set.acc = set.gyro = true;

  minimu9::comm_config config = minimu9::auto_detect(options.i2c_bus_name);

  sensor_set missing = set - minimu9::config_sensor_set(config);
  if (missing)
  {
    if (missing.mag)
    {
      std::cerr << "Error: No magnetometer found." << std::endl;
    }
    if (missing.acc)
    {
      std::cerr << "Error: No accelerometer found." << std::endl;
    }
    if (missing.gyro)
    {
      std::cerr << "Error: No gyro found." << std::endl;
    }
    std::cerr << "Error: Needed sensors are missing." << std::endl;
    return 1;
  }

  config = minimu9::disable_redundant_sensors(config, set);
  
  minimu9::handle imu;
  imu.open(config);
  
  // Figure out the basic operating mode and start running.
  if (options.mode == "raw")
  {
    std::ofstream f;
    // f.open("outfile");
    f.open(options.output_file);
    stream_raw_values(imu, options.samples, options.frequency, f);
    f.close();
  }
  else
  {
    std::cerr << "Unknown mode '" << options.mode << "'" << std::endl;
    return 1;
  }
  imu.show_config();
  return 0;
}

int main(int argc, char ** argv)
{
  try
  {
    main_with_exceptions(argc, argv);
  }
  catch(const std::system_error & error)
  {
    std::string what = error.what();
    const std::error_code & code = error.code();
    std::cerr << "Error: " << what << " (" << code << ")" << std::endl;
    return 2;
  }
  catch(const std::exception & error)
  {
    std::cerr << "Error: " << error.what() << std::endl;
    return 9;
  }
}
