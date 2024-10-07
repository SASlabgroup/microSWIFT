#include "lsm6.h"
#include <stdexcept>
#include <iostream>
#include <unistd.h>

void lsm6::handle::show_config()
{
  uint8_t block[1];
  i2c.write_byte_and_read(config.i2c_address, 0x63, block, sizeof(block));
  int r;
  r=block[0];
  if ( r >= 128 )
  {
    r&=127;
    r-=128;
  }
  std::cout << "INTERNAL_FREQ_FINE : " << r << "\n";
}

void lsm6::handle::open(const comm_config & config)
{
  if (!config.use_sensor)
  {
    throw std::runtime_error("LSM6 configuration is null.");
  }

  this->config = config;
  i2c.open(config.i2c_bus_name);
}

void lsm6::handle::enable(uint16_t s)
{
  if (config.device == LSM6DS33 || config.device == LSM6DSO)
  {
    //// LSM6DS33/LSM6DSO gyro

    // ODR = 1000 (1.66 kHz (high performance))
    // ODR = 0111 (  833 Hz (high performance))
    // ODR = 0110 (  416 Hz (high performance))
    // ODR = 0101 (  208 Hz (high performance))
    // ODR = 0100 (  104 Hz (high performance))
    // ODR = 0011 (   52 Hz (high performance))
    // ODR = 0010 (   26 Hz (high performance))
    // ODR = 0001 (   12_5 Hz (high performance))
    // FS_G = 11 (2000 dps)
    // FS_G = 11 (2000 dps)
    // FS_G = 11 (2000 dps)
    // FS_G = 11 (2000 dps)
    // write_reg(CTRL2_G, 0b10001100); // 1.66 kHz
    // std::cout << " WR : " << int(0b00001100 | (16*s) ) << "\n";
    write_reg(CTRL2_G, 0b00001100 | (16*s) );
    usleep(200000);
    // defaults
    write_reg(CTRL7_G, 0b00000000);
    usleep(200000);
    //// LSM6DS33/LSM6DSO accelerometer

    // ODR = 1000 (1.66 kHz (high performance))
    // ODR = 0111 (  833 Hz (high performance))
    // ODR = 0110 (  416 Hz (high performance))
    // ODR = 0101 (  208 Hz (high performance))
    // ODR = 0100 (  104 Hz (high performance))
    // ODR = 0011 (   52 Hz (high performance))
    // ODR = 0010 (   26 Hz (high performance))
    // ODR = 0001 (   12_5 Hz (high performance))
    // FS_XL = 11 (8 g full scale)
    // write_reg(CTRL1_XL, 0b10001100); // 1.66 kHz
    write_reg(CTRL1_XL, 0b00001100 | (16*s));
    usleep(200000);
    //// common

    // IF_INC = 1 (automatically increment address register)
    write_reg(CTRL3_C, 0b00000100);
    usleep(200000);
  }
  else
  {
    throw std::runtime_error("Cannot enable unknown LSM6 device.");
  }
}

void lsm6::handle::write_reg(reg_addr addr, uint8_t value)
{
  i2c.write_two_bytes(config.i2c_address, addr, value);
}

bool lsm6::handle::data_available()
{
  uint8_t block[1];
  i2c.write_byte_and_read(config.i2c_address, STATUS_REG, block, sizeof(block));
  return (block[0] & 3) > 0;
}

void lsm6::handle::read_gyro()
{
  uint8_t block[6];
  i2c.write_byte_and_read(config.i2c_address, OUTX_L_G, block, sizeof(block));
  g[0] = (int16_t)(block[0] | block[1] << 8);
  g[1] = (int16_t)(block[2] | block[3] << 8);
  g[2] = (int16_t)(block[4] | block[5] << 8);
}

void lsm6::handle::read_acc()
{
  uint8_t block[6];
  i2c.write_byte_and_read(config.i2c_address, OUTX_L_XL, block, sizeof(block));
  a[0] = (int16_t)(block[0] | block[1] << 8);
  a[1] = (int16_t)(block[2] | block[3] << 8);
  a[2] = (int16_t)(block[4] | block[5] << 8);
}
