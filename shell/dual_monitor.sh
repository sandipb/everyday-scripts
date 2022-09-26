#!/bin/bash
LAPTOP="LVDS1"
MONITOR="VGA1"

# RESOLUTION SETTINGS
# This sets your VGA1 monitor to its best resolution.
xrandr --output $LAPTOP --mode 1600x900 --rate 60
# This sets your laptop monitor to its best resolution.
xrandr --output $MONITOR --mode 1920x1200--rate 60

# MONITOR ORDER
# Put the Laptop right, VGA1 monitor left
# xrandr --output VGA1 --left-of LVDS1
# Put the Laptop left, VGA1 monitor right
xrandr --output $LAPTOP --left-of $MONITOR

# PRIMARY MONITOR
# This sets your laptop monitor as your primary monitor.
xrandr --output $MONITOR --primary
# This sets your VGA monitor as your primary monitor.
# xrandr --output VGA1 --primary

