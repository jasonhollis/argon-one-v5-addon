# Argon ONE V5 Home Assistant Add-on

A Home Assistant add-on for the Argon ONE V5 Raspberry Pi 5 case, providing OLED display functionality.

## Features

- OLED display support (128x64)
- Rotating information screens:
  - CPU temperature and fan status
  - System resources (CPU & RAM usage)
  - Home Assistant status and uptime
- Automatic screen rotation every 10 seconds

## Installation

### Method 1: Add Repository to Home Assistant

1. In Home Assistant, navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu → **Repositories**
3. Add this repository URL: `https://github.com/jasonhollis/argon-one-v5-addon`
4. Find "Argon ONE V5" in the add-on store and click **Install**

### Method 2: Manual Installation

1. Copy the `argon_one_v5` folder to your Home Assistant `/addons` directory
2. Restart Home Assistant or reload the add-on store
3. Install the "Argon ONE V5" add-on from the Local add-ons section

## Configuration

No configuration required. The add-on will automatically detect and use the OLED display.

## Hardware Requirements

- Raspberry Pi 5
- Argon ONE V5 case
- Properly connected I2C OLED display

## Known Limitations

- Fan PWM control is currently read-only in Home Assistant OS
- Manual fan control may be required through hardware buttons

## Troubleshooting

### OLED Not Displaying
- Ensure I2C is enabled on your Raspberry Pi
- Check that the OLED is properly connected
- View add-on logs for debugging information

### No Temperature Reading
- Verify `/sys/class/thermal/thermal_zone0/temp` is accessible
- Check add-on logs for errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Argon40 official scripts
- Built for Home Assistant OS
