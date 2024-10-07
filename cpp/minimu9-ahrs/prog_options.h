#pragma once

#include <string>

struct prog_options
{
  bool show_help = false;
  bool show_version = false;
  long samples;
  uint16_t frequency;
  std::string mode;
  std::string output_mode;
  std::string output_file;
  std::string i2c_bus_name;
};

void print_command_line_options_desc();

prog_options get_prog_options(int argc, char ** argv);

