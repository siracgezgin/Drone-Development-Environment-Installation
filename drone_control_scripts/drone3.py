from dronekit import connect, VehicleMode, LocationGlobalRelative
import math
import time
from geopy.distance import distance, distance
from geopy.point import Point

def calculate_target_gps(start_latitude, start_longitude, target_distance_meters, direction):
    # Create a starting point object
    start_point = Point(latitude=start_latitude, longitude=start_longitude)

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
# Function to connect to a drone
def connect_drone(connection_string):
    try:
        vehicle = connect(connection_string, wait_ready=True)
        print("Connected to vehicle on: %s" % connection_string)
        return vehicle
    except Exception as e:
        print("Error connecting to vehicle: %s" % e)
        return None

# Function to arm the drone
def arm_and_takeoff(vehicle, target_altitude):
    print("Arming motors...")
    while not vehicle.is_armable:
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off to %f meters..." % target_altitude)
    vehicle.simple_takeoff(target_altitude)

    while True:
        altitude = vehicle.location.global_relative_frame.alt
        if altitude >= target_altitude * 0.95:
            print("Reached target altitude of %f meters." % target_altitude)
            break
        time.sleep(1)


def print_gps_coordinates(drone):
    current_location = drone.location.global_frame
    print("Current GPS Coordinates:")
    print("Latitude: %.7f" % current_location.lat)
    print("Longitude: %.7f" % current_location.lon)
    print("Altitude: %.2f meters" % current_location.alt)

# Function to command the drone to a GPS position
def goto_position(vehicle, latitude, longitude, altitude):
    target_location = LocationGlobalRelative(latitude, longitude, altitude)
    vehicle.simple_goto(target_location)
    while True:
        current_location = vehicle.location.global_relative_frame
        distance = get_distance_metres(current_location, target_location)
        if distance < 1:
            print("Reached target position.")
            break
        time.sleep(1)

# Function to calculate distance in meters between two GPS coordinates
def get_distance_metres(location1, location2):
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

# Function to control throttle (assuming quadcopter, adjusting throttle directly)
def set_throttle(vehicle, throttle):
    # Assuming throttle range is 0 to 1, adjust according to your setup
    # Example: throttle = 0.5 sets throttle to 50%
    vehicle.channels.overrides['3'] = int(throttle * 1000)

# Example usage:
if __name__ == "__main__":
    # Connect to each drone (replace with your connection strings)
    print("3")
    drone = connect_drone('udp:127.0.0.1:14570')
    
    center_lat = -35.3632620
    center_lon = 149.1652374
    center_alt = 20

    if drone:
        print("Arming and taking off to altitude 20.")
        arm_and_takeoff(drone, 20)
        print("Took off")
        # 5 meter north
        (t_lat, t_lon) = calculate_target_gps(center_lat, center_lon, 5, "north")
        # 8,66 meter west
        (t_lat2, t_lon2) = calculate_target_gps(t_lat, t_lon, 8.66, "east")
        goto_position(drone, t_lat2, t_lon2, center_alt)
        print("Reached destination")

        print_gps_coordinates(drone)    
        