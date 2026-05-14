import time
from collections import deque
from smbus2 import SMBus

MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_SCALE = 16384.0   # ±2g range → LSB/g

def read_word(bus, reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low  = bus.read_byte_data(MPU_ADDR, reg + 1)
    val = (high << 8) | low
    return val - 65536 if val >= 32768 else val   # signed 16-bit

def read_accel(bus):
    x = read_word(bus, ACCEL_XOUT_H)     / ACCEL_SCALE
    y = read_word(bus, ACCEL_XOUT_H + 2) / ACCEL_SCALE
    z = read_word(bus, ACCEL_XOUT_H + 4) / ACCEL_SCALE
    return x, y, z

def main():
    with SMBus(7) as bus: # Jetson Nano uses I2C bus 7
        bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)   # wake from sleep
        window = deque(maxlen=10)                       # ~1 second @ 10Hz
        THRESHOLD_G = 0.6                               # lateral g for "erratic"
        N_REQUIRED  = 4                                 # samples above threshold

        while True:
            x, y, z = read_accel(bus)
            window.append(abs(y))                       # lateral axis
            erratic = sum(v > THRESHOLD_G for v in window) >= N_REQUIRED
            print(f"x={x:+.2f} y={y:+.2f} z={z:+.2f}  erratic={erratic}")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
