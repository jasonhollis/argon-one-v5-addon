## v3.5.0 - 2025-08-03

### Changed
- Completely redesigned OLED screen layouts for better readability
- Screen 1: CPU & THERMAL - Shows temperature, fan status, and CPU load
- Screen 2: MEMORY & DISK - Shows RAM and disk usage with progress bars  
- Screen 3: SYSTEM INFO - Shows IP address, uptime, and system overview
- Fixed progress bar display calculations
- Improved spacing between display elements
- Added real-time reading from system files (/proc, /sys)

### Fixed
- Progress bars now correctly show percentages
- Removed 'N/A' displays by reading directly from system files
