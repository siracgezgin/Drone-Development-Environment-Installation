from dronekit import connect, VehicleMode, LocationGlobalRelative
import math
import time
from geopy.distance import distance, Point

def calculate_target_gps(start_latitude, start_longitude, target_distance_meters, direction):
    start_point = Point(latitude=start_latitude, longitude=start_longitude)
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
    return target_point.latitude, target_point.longitude

def connect_drone(connection_string):
    print(f"Attempting to connect to vehicle on: {connection_string}")
    try:
        vehicle = connect(connection_string, wait_ready=True, timeout=120)
        vehicle.connection_string = connection_string  # connection_string niteliğini ekle
        print(f"Connected to vehicle on: {connection_string}")
        return vehicle
    except Exception as e:
        print(f"Error connecting to vehicle on {connection_string}: {e}")
        return None

def arm_and_takeoff(vehicle, target_altitude):
    print(f"Arming motors for vehicle on {vehicle.connection_string}...")
    while not vehicle.is_armable:
        print(f"Waiting for vehicle on {vehicle.connection_string} to be armable...")
        time.sleep(1)
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        print(f"Waiting for arming on vehicle {vehicle.connection_string}...")
        time.sleep(1)
    print(f"Taking off to {target_altitude} meters on vehicle {vehicle.connection_string}...")
    vehicle.simple_takeoff(target_altitude)
    while True:
        altitude = vehicle.location.global_relative_frame.alt
        if altitude >= target_altitude * 0.95:
            print(f"Reached target altitude of {target_altitude} meters on vehicle {vehicle.connection_string}.")
            break
        time.sleep(1)

def goto_position(vehicle, latitude, longitude, altitude):
    target_location = LocationGlobalRelative(latitude, longitude, altitude)
    vehicle.simple_goto(target_location)
    while True:
        current_location = vehicle.location.global_relative_frame
        dist = get_distance_metres(current_location, target_location)
        if dist < 1:
            print(f"Reached target position on vehicle {vehicle.connection_string}.")
            break
        time.sleep(1)

def get_distance_metres(location1, location2):
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def form_formation(center_lat, center_lon, center_alt, num_drones):
    connection_strings = [
        'udp:127.0.0.1:14550',
        'udp:127.0.0.1:14560',
        'udp:127.0.0.1:14570',
        'udp:127.0.0.1:14580',
        'udp:127.0.0.1:14590'
    ]
    
    drones = []
    angles = [0, 120, 240]  # Üçgen formasyon açıları
    radius = 10  # Formasyonun yarıçapı
    
    for i in range(num_drones):
        if i < len(connection_strings):
            drone = connect_drone(connection_strings[i])
            if drone:
                drones.append(drone)
                time.sleep(5)  # Bir drone havalandıktan sonra bekleme süresi
                arm_and_takeoff(drone, 8)  # 8 metreye kalkma
            else:
                print(f"Drone {i + 1} failed to connect.")
        else:
            print(f"Insufficient connection strings for {num_drones} drones.")
            break
    
    if len(drones) >= 3:
        for i, drone in enumerate(drones):
            angle = angles[i % len(angles)]  # Üçgen formasyon açıları
            x_offset = radius * math.cos(math.radians(angle))
            y_offset = radius * math.sin(math.radians(angle))
            target_lat, target_lon = calculate_target_gps(center_lat, center_lon, x_offset, 'east')
            target_lat, target_lon = calculate_target_gps(target_lat, target_lon, y_offset, 'north')
            goto_position(drone, target_lat, target_lon, 8)
            time.sleep(5)  # Bir drone hedefe ulaştıktan sonra bekleme süresi
    else:
        print("Insufficient number of drones for formation")

if __name__ == "__main__":
    center_lat = -35.3632620
    center_lon = 149.1652374
    center_alt = 8  # Yüksekliği 8 metre olarak ayarladık
    num_drones = 5  # Dron sayısını burada belirleyin
    form_formation(center_lat, center_lon, center_alt, num_drones)
