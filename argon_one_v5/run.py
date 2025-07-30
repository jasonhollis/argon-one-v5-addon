#!/usr/bin/env python3
import time
import os
import sys
import subprocess
import socket

print("Argon ONE V5 addon starting...", flush=True)

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

# Screen rotation timer
SCREEN_DURATION = 10  # seconds per screen
screen_index = 0
screen_timer = time.time()

def get_cpu_temp():
    """Get CPU temperature"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000
        return temp
    except:
        return 0

def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        # Simple CPU usage based on load average
        with open('/proc/loadavg', 'r') as f:
            load1 = float(f.read().split()[0])
        # Assume 4 cores, scale to percentage
        return min(100, int(load1 * 25))
    except:
        return 0

def get_memory_usage():
    """Get memory usage"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1]) // 1024  # MB
            available = int(lines[2].split()[1]) // 1024  # MB
            used = total - available
            percent = int((used / total) * 100)
            return used, total, percent
    except:
        return 0, 0, 0

def get_ip_address():
    """Get the host's IP address from Home Assistant supervisor"""
    try:
        # Try to get from environment variable first
        supervisor_ip = os.environ.get('SUPERVISOR_HOST', '')
        if supervisor_ip:
            return supervisor_ip
        
        # Try to get the default route's IP
        result = subprocess.run(['ip', 'route', 'get', '1.1.1.1'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            # Parse output like: "1.1.1.1 via 172.30.32.1 dev eth0 src 172.30.32.2"
            parts = result.stdout.split()
            if 'src' in parts:
                src_index = parts.index('src')
                if src_index + 1 < len(parts):
                    ip = parts[src_index + 1]
                    # If it's a docker internal IP, try to get the host IP
                    if ip.startswith('172.'):
                        # Read the host IP from /proc/net/route or just show partial
                        return "Host IP"
                    return ip
        
        # Last resort - show that we're in HA
        return "HomeAssistant"
    except:
        return "No Network"

def draw_centered_text(draw, y, text, font=None):
    """Draw centered text"""
    text_width = len(text) * 6  # Approximate
    x = (oled_device.width - text_width) // 2
    draw.text((x, y), text, fill="white", font=font)

def display_screen_1():
    """Screen 1: Temperature and Fan Status"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_centered_text(draw, 0, "ARGON ONE V5")
        
        # Temperature
        temp = get_cpu_temp()
        draw.text((5, 20), f"Temp: {temp:.1f}C", fill="white")
        
        # Fan status (since we can't control it, just show status)
        fan_status = "Manual" if temp > 50 else "Auto"
        draw.text((5, 35), f"Fan: {fan_status}", fill="white")
        
        # Time
        current_time = time.strftime("%H:%M:%S")
        draw.text((5, 50), current_time, fill="white")
        
        oled_device.display(image)
    except Exception as e:
        print(f"Screen 1 error: {e}", flush=True)

def display_screen_2():
    """Screen 2: System Resources"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_centered_text(draw, 0, "SYSTEM")
        
        # CPU Usage
        cpu = get_cpu_usage()
        draw.text((5, 20), f"CPU:  {cpu:3d}%", fill="white")
        
        # Memory Usage
        used, total, percent = get_memory_usage()
        draw.text((5, 35), f"RAM:  {percent:3d}%", fill="white")
        draw.text((5, 50), f"      {used}MB/{total}MB", fill="white")
        
        oled_device.display(image)
    except Exception as e:
        print(f"Screen 2 error: {e}", flush=True)

def display_screen_3():
    """Screen 3: Network Info"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_centered_text(draw, 0, "HOME ASSISTANT")
        
        # Show Home Assistant specific info
        draw.text((5, 20), "Addon: Active", fill="white")
        
        # Show uptime
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                draw.text((5, 35), f"Uptime: {hours}h {minutes}m", fill="white")
        except:
            pass
        
        # Date
        current_date = time.strftime("%Y-%m-%d")
        draw.text((5, 50), current_date, fill="white")
        
        oled_device.display(image)
    except Exception as e:
        print(f"Screen 3 error: {e}", flush=True)

# List of screen functions - only 3 useful screens
screens = [
    display_screen_1,  # Temp & Fan
    display_screen_2,  # System Resources
    display_screen_3   # Home Assistant Status
]

# Main loop
print("Starting display rotation...", flush=True)
loop_count = 0

while True:
    try:
        # Update OLED if available
        if oled_device:
            # Check if it's time to switch screens
            if time.time() - screen_timer >= SCREEN_DURATION:
                screen_index = (screen_index + 1) % len(screens)
                screen_timer = time.time()
            
            # Display current screen
            try:
                screens[screen_index]()
            except Exception as e:
                print(f"Screen {screen_index + 1} display error: {e}", flush=True)
        
        # Log status periodically
        if loop_count % 60 == 0:  # Every minute
            temp = get_cpu_temp()
            cpu = get_cpu_usage()
            _, _, mem = get_memory_usage()
            print(f"Status - Temp: {temp:.1f}°C, CPU: {cpu}%, RAM: {mem}%", flush=True)
        
        loop_count += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"Error in main loop: {e}", flush=True)
        time.sleep(5)
