#!/bin/bash

gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I0"
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I1"
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I2"

sleep 2s

gazebo --verbose ../ardupilot_gazebo/worlds/iris_arducopter_runway_multi.world
