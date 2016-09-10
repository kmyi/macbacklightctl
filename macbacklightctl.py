#!/usr/bin/env python3
# macbacklightctl.py ---
#
# Filename: macbacklightctl.py
# Description:
# Author: Kwang Moo Yi (kwang.m.yi@gmail.com)
# Maintainer:
# Created: Sat Sep 10 17:38:47 2016 (+0200)
# Version:
# Package-Requires: (xbacklight)
# URL:
# Doc URL:
# Keywords:
# Compatibility:
#
#

# Commentary: This is a basic python script that runs as daemon for automatic
# adjustment of the screen backlight using the ambient sensor in mac. Simply
# run this script in the background.
#
#
#
#

# Change Log:
#
#
#

# Code:


from math import log
from random import random
from subprocess import PIPE, Popen, check_output
from time import sleep

############################################################
# configurations

# sleep time in seconds
SLEEP_TIME = 1

# sensor bias
BIAS = 0.0

# sensor truncate value
SENSOR_MAX = 20.0 - 1.0

# minimum backlight value
MIN_BACKLIGHT = 5.

# maximum backlight value
MAX_BACKLIGHT = 100.

############################################################
# code

# wait random amount
sleep(random())

# check if multiple instances are running
psinfo = Popen(("ps", "-ef"), stdout=PIPE)
psgrep = str(check_output(("grep", "python3.*macbacklightctl.py"),
                          stdin=psinfo.stdout), "utf-8")
psmatch = psgrep.split("\n")

# Do nothing if we have another one runnning
if len(psmatch) != 3:
    print("Already running!")
# Keep polling the light information and adjust backlight
else:

    # Max light sensor value in log scale
    lightmax = log(SENSOR_MAX + 1., 2.)

    # Sensor value to control value conversion
    val_to_ctl = (MAX_BACKLIGHT - MIN_BACKLIGHT) / (lightmax + BIAS)

    # Read ambient sensor value to get initial lighting
    with open("/sys/devices/platform/applesmc.768/light",
              "r") as stat_file:
        lightval = int(stat_file.read().lstrip("(").split(",")[0])
        lightval = min([lightval, SENSOR_MAX])

    # Do log scaling
    lightval = (log(float(lightval + 1), 2.) + BIAS) / (lightmax + BIAS)

    # Initial control computation
    new_backlight = MIN_BACKLIGHT + lightval * val_to_ctl

    # set backlight initially
    check_output(("xbacklight", "=", str(int(new_backlight))))

    # Initial sleep
    sleep(SLEEP_TIME)

    while True:

        # update prev_lightval
        prev_lightval = lightval

        # Read ambient sensor value
        with open("/sys/devices/platform/applesmc.768/light",
                  "r") as stat_file:
            lightval = int(stat_file.read().lstrip("(").split(",")[0])
            lightval = min([lightval, SENSOR_MAX])

        # Do log scaling
        lightval = (log(float(lightval + 1), 2.) + BIAS) / (lightmax + BIAS)

        # If lightlevel changed
        if lightval != prev_lightval:
            # adjust it to get the new value
            new_backlight = MIN_BACKLIGHT + lightval * val_to_ctl
            # set backlight
            check_output(("xbacklight", "=", str(int(new_backlight))))

        # sleep
        sleep(SLEEP_TIME)
#
# macbacklightctl.py ends here
