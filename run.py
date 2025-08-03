#!/usr/bin/env python3
import time
import os
import sys
import json
from datetime import datetime
import pytz

print("Argon ONE V5 addon starting (v3.5)...", flush=True)

# Set timezone
TIMEZONE = pytz.timezone('Australia/Melbourne')

# Get configuration
try:
    with open('/data/options.json') as f:
        config = json.load(f)
except:
    config = {}

SCREEN_DURATION = config.get('screen_duration', 10)

# System readers
def get_cpu_temp():
    """Get CPU temperature"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000
        return f"{temp:.1f}°C"
    except:
        return "N/A"

def get_cpu_usage():
    """Get CPU usage from load average"""
    try:
        with open('/proc/loadavg', 'r') as f:
            load1 = float(f.read().split()[0])
        cpu_percent = min(100, int(load1 * 25))  # Assume 4 cores
        return cpu_percent
    except:
        return 0

def get_memory_info():
    """Get memory usage"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1]) // 1024  # MB
            available = int(lines[2].split()[1]) // 1024  # MB
            used = total - available
            percent = int((used / total) * 100)
            return percent, f"{used}/{total}MB"
    except:
        return 0, "N/A"

def get_disk_usage():
    """Get disk usage"""
    try:
        stat = os.statvfs('/')
        total = (stat.f_blocks * stat.f_frsize) // (1024**3)  # GB
        free = (stat.f_bavail * stat.f_frsize) // (1024**3)   # GB
        used = total - free
        percent = int((used / total) * 100)
        return percent, f"{free}GB"
    except:
        return 0, "N/A"

def get_uptime():
    """Get system uptime"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            if days > 0:
                return f"{days}d {hours}h"
            else:
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
    except:
        return "N/A"

def get_ip_address():
    """Get primary IP address"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

# Try to import OLED libraries
oled_device = None
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from PIL import Image, ImageDraw, ImageFont
    
    print("OLED libraries loaded successfully", flush=True)
    
    # Initialize OLED
    serial = i2c(port=1, address=0x3C)
    oled_device = ssd1306(serial)
    print(f"OLED initialized: {oled_device.width}x{oled_device.height}", flush=True)
    
except Exception as e:
    print(f"OLED initialization failed: {e}", flush=True)
    sys.exit(1)

def draw_progress_bar(draw, x, y, width, height, percent):
    """Draw a progress bar with correct fill"""
    # Draw border
    draw.rectangle((x, y, x + width, y + height), outline=1, fill=0)
    
    # Calculate fill width correctly
    percent = max(0, min(100, percent))
    inner_width = width - 2
    fill_width = int(inner_width * percent / 100)
    
    # Draw fill if there's something to show
    if fill_width > 0:
        draw.rectangle((x + 1, y + 1, x + fill_width, y + height - 1), fill=1)

def display_cpu_screen():
    """Display CPU and temperature info"""
    if not oled_device:
        return
    
    try:
        image = Image.new('1', (128, 64), 0)
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((0, 0), "CPU & THERMAL", fill=1)
        draw.line([(0, 10), (127, 10)], fill=1)
        
        # CPU temp with larger font
        temp = get_cpu_temp()
        temp_val = float(temp.rstrip('°C'))
        draw.text((0, 16), f"Temp: {temp}", fill=1)
        
        # Fan status
        if temp_val > 65:
            fan_status = "Fan: HIGH"
        elif temp_val > 50:
            fan_status = "Fan: MEDIUM"
        elif temp_val > 40:
            fan_status = "Fan: LOW"
        else:
            fan_status = "Fan: OFF"
        draw.text((70, 16), fan_status, fill=1)
        
        # CPU load with bar
        cpu = get_cpu_usage()
        draw.text((0, 32), f"Load: {cpu}%", fill=1)
        draw_progress_bar(draw, 50, 32, 75, 6, cpu)
        
        # Time at bottom
        mel_time = datetime.now(TIMEZONE)
        draw.text((0, 54), mel_time.strftime("%H:%M"), fill=1)
        draw.text((70, 54), mel_time.strftime("%d/%m"), fill=1)
        
        oled_device.display(image)
        
    except Exception as e:
        print(f"CPU screen error: {e}", flush=True)

def display_memory_screen():
    """Display memory and storage info"""
    if not oled_device:
        return
    
    try:
        image = Image.new('1', (128, 64), 0)
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((0, 0), "MEMORY & DISK", fill=1)
        draw.line([(0, 10), (127, 10)], fill=1)
        
        # Memory with bar
        mem_percent, mem_usage = get_memory_info()
        draw.text((0, 16), f"RAM: {mem_percent}%", fill=1)
        draw_progress_bar(draw, 50, 16, 75, 6, mem_percent)
        draw.text((0, 24), f"({mem_usage})", fill=1)
        
        # Disk usage with bar
        disk_percent, disk_free = get_disk_usage()
        draw.text((0, 36), f"Disk: {disk_percent}%", fill=1)
        draw_progress_bar(draw, 50, 36, 75, 6, disk_percent)
        draw.text((0, 44), f"Free: {disk_free}", fill=1)
        
        # Time at bottom
        mel_time = datetime.now(TIMEZONE)
        draw.text((0, 54), mel_time.strftime("%H:%M"), fill=1)
        draw.text((70, 54), mel_time.strftime("%d/%m"), fill=1)
        
        oled_device.display(image)
        
    except Exception as e:
        print(f"Memory screen error: {e}", flush=True)

def display_system_screen():
    """Display system overview"""
    if not oled_device:
        return
    
    try:
        image = Image.new('1', (128, 64), 0)
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((0, 0), "SYSTEM INFO", fill=1)
        draw.line([(0, 10), (127, 10)], fill=1)
        
        # IP Address
        ip = get_ip_address()
        draw.text((0, 16), f"IP: {ip}", fill=1)
        
        # Uptime
        uptime = get_uptime()
        draw.text((0, 28), f"Up: {uptime}", fill=1)
        
        # Quick stats
        temp = get_cpu_temp()
        cpu = get_cpu_usage()
        mem, _ = get_memory_info()
        draw.text((0, 40), f"CPU:{cpu}% RAM:{mem}% {temp}", fill=1)
        
        # Date/time with day
        mel_time = datetime.now(TIMEZONE)
        draw.text((0, 54), mel_time.strftime("%H:%M"), fill=1)
        draw.text((45, 54), mel_time.strftime("%a %d %b"), fill=1)
        
        oled_device.display(image)
        
    except Exception as e:
        print(f"System screen error: {e}", flush=True)

# Screen list
SCREENS = [
    display_cpu_screen,
    display_memory_screen,
    display_system_screen
]

# Main loop
print("Starting display loop...", flush=True)
screen_index = 0
screen_timer = time.time()
loop_count = 0

while True:
    try:
        if oled_device:
            # Check if it's time to switch screens
            if time.time() - screen_timer >= SCREEN_DURATION:
                screen_index = (screen_index + 1) % len(SCREENS)
                screen_timer = time.time()
            
            # Display current screen
            SCREENS[screen_index]()
        
        # Log status periodically
        if loop_count % 60 == 0:  # Every minute
            mel_time = datetime.now(TIMEZONE)
            temp = get_cpu_temp()
            cpu = get_cpu_usage()
            mem, _ = get_memory_info()
            disk, _ = get_disk_usage()
            ip = get_ip_address()
            print(f"[{mel_time.strftime('%H:%M')}] {ip} - CPU: {temp} {cpu}%, RAM: {mem}%, Disk: {disk}%", flush=True)
        
        loop_count += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"Error in main loop: {e}", flush=True)
        time.sleep(5)
