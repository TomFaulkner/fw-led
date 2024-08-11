import time
import fcntl
import os
import signal


def watch_dir(dirname, handler):
    signal.signal(signal.SIGIO, handler)
    fd = os.open(dirname, os.O_RDONLY)
    fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
    fcntl.fcntl(
        fd, fcntl.F_NOTIFY, fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT
    )


def prep_dir(dirname, interactive=True):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    if os.listdir(dirname):
        print("Directory not empty")
        print(f"Contents: {os.listdir(dirname)}")
        if not interactive:
            exit(1)
        cont = input("Y to continue, directory contents will be erased: ")
        if cont != "Y":
            exit(1)
        for f in os.listdir(dirname):
            os.remove(dirname + "/" + f)


if __name__ == "__main__":
    FNAME = "/home/tom/touchme"
    prep_dir(FNAME, interactive=True)

    def handler(signum, frame):
        print("File %s modified" % (FNAME,))
        files = os.listdir(FNAME)
        print(files)
        if "brightness" in files:
            with open(FNAME + "/brightness", "r") as f:
                print(f.read())

    watch_dir(FNAME, handler)

    while True:
        time.sleep(1000)
