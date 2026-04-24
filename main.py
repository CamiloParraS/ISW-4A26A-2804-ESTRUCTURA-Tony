from clock import AnalogClockBase


if __name__ == "__main__":
    clock = AnalogClockBase()
    print(clock.hour_path.sequence())
