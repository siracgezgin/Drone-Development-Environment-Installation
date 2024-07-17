from pymavlink import mavutil
import time

# Pixhawk ile bağlantı kurun
master = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)

# ArduPilot'un başlatılmasını bekleyin
master.wait_heartbeat()

# Motor çalıştırma fonksiyonları
def set_servo(channel, pwm_value):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        channel,    # Servo çıkış kanalı (1-16)
        pwm_value,  # PWM değeri (1000-2000 arası)
        0, 0, 0, 0, 0
    )

# Motoru çalıştır ve durdurma örnekleri
try:
    while True:
        set_servo(1, 1600)  # Motoru çalıştır (örnek PWM değeri)
        time.sleep(5)
        set_servo(1, 1000)  # Motoru durdur
        time.sleep(2)
except KeyboardInterrupt:
    pass
