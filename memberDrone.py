import socket
import threading
import datetime
import sys
import os
import signal
import subprocess
import time

from dronekit import connect, VehicleMode, LocationGlobalRelative
import math
from geopy.distance import distance, distance
from geopy.point import Point
import numpy as np

HOST = '127.0.0.1'  
PORT = 3350 

now = datetime.datetime.now()

# Aracınıza bağlanın )
print("Araca bağlanılıyor...")
vehicle = connect('/dev/ttyACM0', wait_ready=True)

graphProcess = None
mainProcess = None

socketOn = False

hostname = socket.gethostname()
localIp = socket.gethostbyname(hostname)

if len(sys.argv) < 2:
    print("Invalid argument count, atleast one parameter should be given.")
    exit()

groundAddress = sys.argv[1]

graphCmd = "./astar graphFile usedNodeFile"
mainCmd = f"python3 mainDrone.py {groundAddress}"


tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tempSocket.connect((groundAddress, 2350))

tempMsg = "NEWMEMBER"

tempSocket.send(tempMsg.encode("utf-8"))

tempSocket.close()



# Dron'un başka bir drone'a ve ya yer istasyonuna göndermek için kullandığı fonksiyon.
# Veri gönderme işini bir fonksiyon içinde yapmamızın nedeni okunabilirliği arttırmak ve
# gönderilen paketlerin yer istasyonunda kaydını tutmak için yazacağımız koda zemin hazırlamak.

def sendMessage(sck, msg):
    sck.send(msg.encode('utf-8'))

# ---------------------------- Özet ---------------------------------
# Senden pixhawk ile veri alışverişi fonksiyonlarını doldurmanı istiyorum.
# Yapılcak işleri aşağıda fonksiyonlara böldüm. Her iş için fonksiyonların gövdelerini kullanabilirsin.
# Fonksiyonlara parametre ekleyip çıkarabilirsin. Özellikle ihtiyacın olacak!
# Başka kütüphaneler import edebilirsin.
# Tekrar eden işler için yeni fonksiyonlarda tanımlayabilirsin.
# -------------------------- Mesaj Formatı --------------------------------
# Dronlar arasındaki haberleşmeyi soyutlayabildiğim kadar soyutladım.
# Sana düşen istenilen verileri yukarında tanımladığım sendMessage fonksiyonu ile göndermen.
# İlk parametre gönderilecek dronun ile kurulan bağlantının socket değişkeni.
# İkinci parametre göndereceğin mesaj. Gönderilecek mesaj noktalı virgül ile ayrılmalı
# Örneğin GPS koordinatı için iki tane verimiz var. Lattitude ve Longtitude. Bunları "Lattitude;Longtitude" diye göndereceğiz. Yine örnek olarak "49.3324;52.4343" gibi.
# HOST değişkeni ana dron'un adresi.
# Dron değiştiği zaman aşağıdaki changeMain fonksiyonu bu adresi güncelleyeceği için, bu adres güncel olacak.


def calculate_target_gps(start_latitude, start_longitude, target_distance_meters, direction):
    # Create a starting point object
    start_point = Point(latitude=start_latitude, longitude=start_longitude)

    print(direction)

    # Calculate target point using Vincenty's formula
    if direction.lower() == 'north':
        target_point = distance(meters=target_distance_meters).destination(start_point, 0)
    elif direction.lower() == 'south':
        target_point = distance(meters=target_distance_meters).destination(start_point, 180)
    elif direction.lower() == 'east':
        target_point = distance(meters=target_distance_meters).destination(start_point, 90)
    elif direction.lower() == 'west':
        target_point = distance(meters=target_distance_meters).destination(start_point, 270)
    else:
        raise ValueError("Direction must be one of: 'north', 'south', 'east', 'west'.")

    # Extract latitude and longitude from the target point
    target_latitude, target_longitude = target_point.latitude, target_point.longitude

    return target_latitude, target_longitude

# Function to calculate distance in meters between two GPS coordinates
def get_distance_metres(location1, location2):
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def arm():
    """
    Aracı silahlandırır ve hedef irtifaya uçurur.
    """
    print("Motorlara güç veriliyor")
    while not vehicle.is_armable:
        print(" Aracın başlatılması bekleniyor (is_armable=false)...")
        print(f" GPS: {vehicle.gps_0}, Batarya: {vehicle.battery}, Mod: {vehicle.mode}")
        time.sleep(0.5)

    print("Motorlara güç aktarımı bekleniyor")
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode != "GUIDED":
        print(" GUIDED moduna geçiş bekleniyor...")
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(0.5)

    vehicle.armed = True

    while not vehicle.armed:
        print(" Güç aktarımı bekleniyor (armed=false)...")
        vehicle.armed = True
        time.sleep(0.5)

    print(str(now.time()) +  f": Arm success!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "ARMSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False

def land():
    vehicle.mode = VehicleMode("LAND")
    while vehicle.mode != "LAND":
        print(" LAND moduna geçiş bekleniyor...")
        vehicle.mode = VehicleMode("LAND")
        time.sleep(0.5)

def takeoff(target_altitude):
    print(f"Kalkış emri alındı: {target_altitude} metre")
    vehicle.simple_takeoff(target_altitude) 

    while True:
        print(" İrtifa: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= float(target_altitude) * 0.95:
            print("Hedef irtifaya ulaşıldı")
            break
        time.sleep(0.5)
    
    print(str(now.time()) +  f": Takeoff success!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "TAKEOFFSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False

def goto_position(vehicle, latitude, longitude, altitude):
    target_location = LocationGlobalRelative(latitude, longitude, altitude)
    vehicle.simple_goto(target_location)
    while True:
        current_location = vehicle.location.global_relative_frame
        distance = get_distance_metres(current_location, target_location)
        print(distance)

        if distance < 1.5:
            print("Reached target position.")
            break
        time.sleep(1)



# GPS koordinatlarını gönderecek fonksiyon. 
def reportGPS(socket):
    current_location = vehicle.location.global_frame
    msg = f"{current_location.lat};{current_location.lon}"
    sock.send(msg.encode("utf-8"))
    return


# Yüksekliği gönderecek fonksiyon
def reportAltitude(socket):
    current_location = vehicle.location.global_frame
    msg = f"{current_location.alt}"
    sock.send(msg.encode("utf-8"))
    return

# Yerdeki sabit UWB'lere olan uzaklığa göre kendi konumunu hesaplayan ve gönderen fonksiyon.
# Şuan UWB'lerimiz çalışmadığı için doldurmana gerek yok. 
# Eğer her şeyi bitirdikten sonra canın sıkılırsa, UWB'ler varmış gibi kodu doldurabilirsin, sana kalmış. 
def reportRelationalCoordinate(socket):
    msg = "5.0;6.0;3.0"
    sock.send(msg.encode("utf-8"))
    return  


# Bu dron'u ana dron olarak tayin eden fonksiyon. Ben dolduracağım
def InitMainDrone(socket):
    

    graphProcess = subprocess.Popen(graphCmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
    mainProcess = subprocess.Popen(mainCmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)

    return

# Yeni ana dron'un IP adresini kaydeden fonksiyon. Yapılacak bir şey yok.
def changeMain(socket, addr):
    HOST = addr[0]
    if HOST != localIp:
        os.killpg(os.getpgid(graphProcess.pid), signal.SIGTERM)
        os.killpg(os.getpgid(mainProcess.pid), signal.SIGTERM)

    return

# Ana dron'dan, gidilecek rotayı alan ve rota üzerinde yol almayı sağlayacak fonksiyon. Daha sonra yapılacak.
def recieveTask(socket, wayList):

    wayLines = wayList.split('\n')
    wayPoints = []
    for line in wayLines:
        wayPoints.append(line.split(' '))

    goto(wayPoints)



    return


def goto(coordArr):

    # coordArr[0] = (x,y,z)
    
    


    return

def goto_direction(socket, distance, direction):
    socket.close()
    socketOn = False

    current_location = vehicle.location.global_frame
    (t_lat, t_lon) = calculate_target_gps(current_location.lat, current_location.lon, distance, direction)
    goto_position(vehicle, t_lat, t_lon, current_location.alt)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "GOTOTASKSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False




    return



# ----------------------------------------------------------------------------------------------------------------------------------------------
# Bu kısımdan sonrası gelen mesajlara göre çağrılması gereken fonksiyonu çağıran kod.
# Daha hiç çalıştırmadım, hata var mı yok mu bilmiyorum.
# Hata yoksa ellemene gerek yok, aksi takdirde ya bana yaz ya da kendin düzelt. Keyfine kalmış.

# BİLEĞİNE KUVVET HADİ :^*

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', PORT))
s.listen()


while True:
    

    sock, addr = s.accept()

    print(str(now.time()) +  f": New connection established with {sock.getpeername()}\n")


    try:
        message = sock.recv(1024).decode('utf-8')

        if not message:
            continue
        
        msgArray = message.split(';')

        print(str(now.time()) +  f": Recieved message from {sock.getpeername()}: {message}\n")

        if msgArray[0] == "REPORTGPS":
            print(str(now.time()) +  f": GPS report request from {sock.getpeername()}\n")
            reportGPS(sock)
        elif msgArray[0] == "REPORTALTITUDE":
            print(str(now.time()) +  f": Altitude report request from {sock.getpeername()}\n")
            reportAltitude(sock)
        elif msgArray[0] == "REPORTRELATIONALCOORDINATE":
            print(str(now.time()) +  f": Relational coordinate report request from {sock.getpeername()}\n")
            reportRelationalCoordinate(sock)
        elif msgArray[0] == "BECOMEMAIN":
            print(str(now.time()) +  f": Main drone change request from {sock.getpeername()}\n")
            InitMainDrone(sock)
        elif msgArray[0] == "NEWMAIN":
            print(str(now.time()) +  f": New main drone information recieved from {sock.getpeername()}\n")
            changeMain(sock, addr)         
        elif msgArray[0] == "GOTO":
            print(str(now.time()) +  f": New task route recieved from {sock.getpeername()}\n")
            recieveTask(sock, msgArray[1])
        elif msgArray[0] == "GOTODIRECTION":
            print(str(now.time()) +  f": New task route recieved from {sock.getpeername()} on {msgArray[2]} for {msgArray[1]} m\n")
            goto_direction(sock, msgArray[1], msgArray[2])
        elif msgArray[0] == "ARM":
            print(str(now.time()) +  f": Arm request recieved from {sock.getpeername()}\n")
            sock.close()
            socketOn = False
            arm()
        elif msgArray[0] == "TAKEOFF":
            print(str(now.time()) +  f": Takeoff request recieved from {sock.getpeername()} for altitude {msgArray[1]} m\n")
            sock.close()
            socketOn = False
            takeoff(msgArray[1])
        elif msgArray[0] == "REPORTVOLTAGE":
            print(str(now.time()) +  f": Voltage level request recieved from {sock.getpeername()}\n")
            voltageLevel = vehicle.battery.voltage
            sock.send(str(voltageLevel).encode("utf-8"))

        elif msgArray[0] == "CONNECTIONTEST":
            print(str(now.time()) +  f": Connection test requested from {sock.getpeername()}\n")
        elif msgArray[0] == "TEST":
            time.sleep(2)
        elif msgArray[0] == "LAND":
            print(str(now.time()) +  f": Landing requested from {sock.getpeername()}\n")
            land()
        else:
            print(str(now.time()) +  f": Unable to interpret message from {sock.getpeername()}: {message}\n")

                



        
    except:
        print(str(now.time()) +  f": Connection error with: {sock.getpeername()}\n")
    finally:
        
        if socketOn:
            print(str(now.time()) +  f": Connection closed from {sock.getpeername()}\n")
            sock.close()
            socketOn = False
    
    



