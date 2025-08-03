# Argon ONE V5 Home Assistant Add-on

Controls the OLED display and fan on the Argon ONE V5 case for Raspberry Pi 5.

## What It Does

- Shows system info on the OLED display
- Controls the fan based on CPU temperature
- Rotates through 3 screens automatically

## Installation

1. Add this repository to Home Assistant: `https://github.com/jasonhollis/argon-one-v5-addon`
2. Install "Argon ONE V5" from the add-on store
3. Start the add-on

## OLED Screens

1. **CPU & THERMAL** - Temperature and fan status
2. **MEMORY & DISK** - RAM and storage usage  
3. **SYSTEM INFO** - IP address and uptime

## Fan Control

- OFF: Below 40°C
- LOW: 40-50°C
- MEDIUM: 50-65°C
- HIGH: Above 65°C

Version 3.5.0
