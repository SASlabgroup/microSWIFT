# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.5

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/brodsky/mocca/ops/libs/RTIMULib2/Linux

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build

# Include any dependencies generated for this target.
include RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/depend.make

# Include the progress variables for this target.
include RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/progress.make

# Include the compile flags for this target's objects.
include RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make

RTIMULibDemo/ui_RTIMULibDemo.h: ../RTIMULibDemo/RTIMULibDemo.ui
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Generating ui_RTIMULibDemo.h"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/lib/x86_64-linux-gnu/qt4/bin/uic -o /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo/ui_RTIMULibDemo.h /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/RTIMULibDemo.ui

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o: ../RTIMULibDemo/AccelCalDlg.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/AccelCalDlg.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/AccelCalDlg.cpp > CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/AccelCalDlg.cpp -o CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o: ../RTIMULibDemo/RTIMULibDemo.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/RTIMULibDemo.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/RTIMULibDemo.cpp > CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/RTIMULibDemo.cpp -o CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o: ../RTIMULibDemo/IMUThread.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/IMUThread.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/IMUThread.cpp > CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/IMUThread.cpp -o CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o: ../RTIMULibDemo/MagCalDlg.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/MagCalDlg.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/MagCalDlg.cpp > CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/MagCalDlg.cpp -o CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o: ../RTIMULibDemo/SelectIMUDlg.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectIMUDlg.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectIMUDlg.cpp > CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectIMUDlg.cpp -o CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o: ../RTIMULibDemo/SelectFusionDlg.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_7) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectFusionDlg.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectFusionDlg.cpp > CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/SelectFusionDlg.cpp -o CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o: ../RTIMULibDemo/main.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_8) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/main.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/main.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/main.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/main.cpp > CMakeFiles/RTIMULibDemo.dir/main.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/main.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo/main.cpp -o CMakeFiles/RTIMULibDemo.dir/main.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o


RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/flags.make
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o: RTIMULibDemo/RTIMULibDemo_automoc.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_9) "Building CXX object RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o -c /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo/RTIMULibDemo_automoc.cpp

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.i"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo/RTIMULibDemo_automoc.cpp > CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.i

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.s"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo/RTIMULibDemo_automoc.cpp -o CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.s

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.requires:

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.provides: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.requires
	$(MAKE) -f RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.provides.build
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.provides

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.provides.build: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o


# Object files for target RTIMULibDemo
RTIMULibDemo_OBJECTS = \
"CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/main.cpp.o" \
"CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o"

# External object files for target RTIMULibDemo
RTIMULibDemo_EXTERNAL_OBJECTS =

RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build.make
RTIMULibDemo/RTIMULibDemo: RTIMULib/libRTIMULib.so.8.0.0
RTIMULibDemo/RTIMULibDemo: /usr/lib/x86_64-linux-gnu/libQtGui.so
RTIMULibDemo/RTIMULibDemo: /usr/lib/x86_64-linux-gnu/libQtCore.so
RTIMULibDemo/RTIMULibDemo: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_10) "Linking CXX executable RTIMULibDemo"
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/RTIMULibDemo.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build: RTIMULibDemo/RTIMULibDemo

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/build

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/AccelCalDlg.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/IMUThread.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/MagCalDlg.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectIMUDlg.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/SelectFusionDlg.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/main.cpp.o.requires
RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires: RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/RTIMULibDemo_automoc.cpp.o.requires

.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/requires

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/clean:
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo && $(CMAKE_COMMAND) -P CMakeFiles/RTIMULibDemo.dir/cmake_clean.cmake
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/clean

RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/depend: RTIMULibDemo/ui_RTIMULibDemo.h
	cd /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/brodsky/mocca/ops/libs/RTIMULib2/Linux /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/RTIMULibDemo /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo /home/brodsky/mocca/ops/libs/RTIMULib2/Linux/build/RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : RTIMULibDemo/CMakeFiles/RTIMULibDemo.dir/depend

