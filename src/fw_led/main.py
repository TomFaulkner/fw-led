import os
import pathlib
import random

import psutil
from inputmodule.cli import find_devs

from fw_led import led
from fw_led import file_monitor

brightness_multiplier = 100


def brightness_monitor(path):
    def handler(signum, frame):
        global brightness_multiplier
        print("File %s modified" % (path,))
        files = os.listdir(path)
        print(files)
        if "brightness" in files:
            with open(path / "brightness", "r") as f:
                try:
                    brightness_multiplier = int(f.read())
                except ValueError:
                    print("Invalid brightness value")
                    return

    return handler


def main():
    path = pathlib.Path.cwd() / "brightness"
    print("Watching path: ", path)
    file_monitor.prep_dir(path, interactive=False)
    file_monitor.watch_dir(path, brightness_monitor(path))
    dev = find_devs()[0]

    with led.S(dev.device) as s:
        while True:
            matrix = led.eq(
                [
                    random.randint(0, 34),
                    round(psutil.virtual_memory().percent // 34),
                    random.randint(0, 34),
                    round(min(psutil.cpu_percent(interval=None) / 34, 3)),
                    round(psutil.sensors_battery().percent // 34),
                    random.randint(0, 34),
                    random.randint(0, 34),
                    random.randint(0, 34),
                    random.randint(0, 34),
                ],
                brightness_multiplier,
            )
            led.draw_matrix(dev, s, matrix)


if __name__ == "__main__":
    main()
