import pymem
import pymem.process
import time
import requests

PROCESS_NAME = "Bigfoot-Win64-Shipping.exe"
BASE_OFFSET = 0x0482BB00
POINTER_OFFSETS = [0x30, 0x228, 0x380, 0x538, 0xB8]  # Last offset is for the float value
API_URL = "http://127.0.0.1:8000/damage"  # Change if FastAPI runs elsewhere

MIN_TIME = 0.5
MAX_TIME = 2.0
MAX_HEALTH_LOSS = 20.0  # Maximum health loss to consider for time mapping


def health_to_time(damage):
    # Clamp damage to [0, MAX_HEALTH_LOSS]
    damage = max(0, min(damage, MAX_HEALTH_LOSS))
    # Linear mapping
    return MIN_TIME + (MAX_TIME - MIN_TIME) * (damage / MAX_HEALTH_LOSS)


def main():
    prev_health = None
    while True:
        try:
            pm = pymem.Pymem(PROCESS_NAME)
            module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
            if module is None:
                time.sleep(1)
                continue
            base_address = module.lpBaseOfDll
            while True:
                try:
                    addr = int(base_address) + BASE_OFFSET
                    addr = int(pm.read_ulonglong(addr))
                    for offset in POINTER_OFFSETS[:-1]:
                        addr = int(pm.read_ulonglong(addr + offset))
                    health_addr = addr + POINTER_OFFSETS[-1]
                    health = float(pm.read_float(health_addr))
                    print(f"health: {health}", end="\r")
                    if prev_health is not None and health < prev_health:
                        damage = prev_health - health
                        t = health_to_time(damage)
                        try:
                            requests.get(API_URL, params={"time": t}, timeout=0.5)
                        except Exception:
                            pass  # Ignore network errors
                    prev_health = health
                    time.sleep(0.2)
                except KeyboardInterrupt:
                    return
                except Exception:
                    time.sleep(1)
                    break
        except Exception:
            time.sleep(1)


if __name__ == "__main__":
    main()
