#!/bin/bash

# Her MAVproxy oturumu başlattığımızda bir süre beklememiz gerekiyor. Aksi takdirde port'lar ile ilgili hata alırsınız.
# Beklenmesi gereken süre bilgisayar hızına göre değişiklik gösterir


gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I0" # ilk drone için MAVproxy 
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I1" # ikinci drone için MAVproxy 
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I2" # üçüncü drone için MAVproxy 
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I3" # dördüncü drone için MAVproxy 
sleep 1s
gnome-terminal -- sh -c "sim_vehicle.py -v ArduCopter -f gazebo-iris --console -I4" # beşinci drone için MAVproxy 

# Gazebo çalışmadan önce MAVproxy oturumlarının başlamasını beklememiz gerekiyor. Aksi takdirde gazebo'da kullandığımız plugin'ler başlattığımız oturumları görmez.
sleep 3s

gazebo --verbose ../ardupilot_gazebo/worlds/iris_arducopter_runway.world
