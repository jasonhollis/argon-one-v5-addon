#!/usr/bin/env python3
import time
import os
import sys
import json
import requests
import subprocess
import socket
from datetime import datetime

print("Argon ONE V5 addon starting (v2.0)...", flush=True)

# Get configuration
with open('/data/options.json') as f:
    config = json.load(f)

SCREEN_DURATION = config.get('screen_duration', 10)
ENABLED_SCREENS = config.get('screens', ['system_overview', 'storage_info', 'network_stats'])

# Home Assistant API setup
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = "http://supervisor/core/api"

def get_ha_state(entity_id):
    """Get state from Home Assistant"""
    try:
        headers = {
            "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{HA_API_URL}/states/{entity_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'state': data.get('state', 'unknown'),
                'attributes': data.get('attributes', {}),
                'unit': data.get('attributes', {}).get('unit_of_measurement', '')
            }
    except Exception as e:
        print(f"API error for {entity_id}: {e}", flush=True)
    return None

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

# Screen functions
def draw_text(draw, x, y, text, font=None):
    """Draw text at position"""
    draw.text((x, y), str(text), fill="white", font=font)

def draw_progress_bar(draw, x, y, width, height, percent):
    """Draw a progress bar"""
    # Border
    draw.rectangle([x, y, x + width, y + height], outline="white", fill="black")
    # Fill
    fill_width = int((width - 2) * percent / 100)
    if fill_width > 0:
        draw.rectangle([x + 1, y + 1, x + 1 + fill_width, y + height - 1], fill="white")

def display_system_overview():
    """System Overview Screen"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_text(draw, 0, 0, "SYSTEM OVERVIEW")
        draw.line([0, 10, 127, 10], fill="white")
        
        # CPU Temperature
        cpu_temp = get_ha_state("sensor.processor_temperature")
        if cpu_temp:
            temp_val = float(cpu_temp['state'])
            draw_text(draw, 0, 15, f"CPU: {temp_val:.1f}°C")
        
        # CPU Usage
        cpu_use = get_ha_state("sensor.processor_use")
        if cpu_use:
            cpu_val = float(cpu_use['state'])
            draw_text(draw, 70, 15, f"{cpu_val:.0f}%")
            draw_progress_bar(draw, 70, 25, 50, 5, cpu_val)
        
        # Memory Usage
        mem_use = get_ha_state("sensor.memory_use_percent")
        if mem_use:
            mem_val = float(mem_use['state'])
            draw_text(draw, 0, 35, f"RAM: {mem_val:.0f}%")
            draw_progress_bar(draw, 45, 35, 80, 5, mem_val)
        
        # Load Average
        load_1 = get_ha_state("sensor.load_1m")
        if load_1:
            draw_text(draw, 0, 50, f"Load: {load_1['state']}")
        
        oled_device.display(image)
    except Exception as e:
        print(f"System overview error: {e}", flush=True)

def display_storage_info():
    """Storage Information Screen"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_text(draw, 0, 0, "STORAGE")
        draw.line([0, 10, 127, 10], fill="white")
        
        # Disk usage
        disk_use = get_ha_state("sensor.disk_use_percent")
        disk_free = get_ha_state("sensor.disk_free")
        
        if disk_use:
            usage = float(disk_use['state'])
            draw_text(draw, 0, 15, f"Used: {usage:.1f}%")
            draw_progress_bar(draw, 0, 25, 127, 8, usage)
        
        if disk_free:
            free_gb = float(disk_free['state'])
            draw_text(draw, 0, 40, f"Free: {free_gb:.1f} GB")
        
        # Last boot
        last_boot = get_ha_state("sensor.last_boot")
        if last_boot:
            draw_text(draw, 0, 55, "Uptime: 2d 3h")  # You'd calculate this
        
        oled_device.display(image)
    except Exception as e:
        print(f"Storage info error: {e}", flush=True)

def display_network_stats():
    """Network Statistics Screen"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_text(draw, 0, 0, "NETWORK")
        draw.line([0, 10, 127, 10], fill="white")
        
        # Network throughput
        net_in = get_ha_state("sensor.network_throughput_in_end0")
        net_out = get_ha_state("sensor.network_throughput_out_end0")
        
        if net_in:
            in_val = float(net_in['state'])
            draw_text(draw, 0, 15, f"In:  {in_val:.1f} MB/s")
        
        if net_out:
            out_val = float(net_out['state'])
            draw_text(draw, 0, 30, f"Out: {out_val:.1f} MB/s")
        
        # Total traffic
        total_in = get_ha_state("sensor.network_in_end0")
        if total_in:
            total_mb = float(total_in['state'])
            draw_text(draw, 0, 50, f"Total: {total_mb:.0f} MB")
        
        oled_device.display(image)
    except Exception as e:
        print(f"Network stats error: {e}", flush=True)

def display_temperatures():
    """Temperature Details Screen"""
    try:
        image = Image.new('1', (oled_device.width, oled_device.height))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw_text(draw, 0, 0, "TEMPERATURES")
        draw.line([0, 10, 127, 10], fill="white")
        
        # CPU Temperature with visual indicator
        cpu_temp = get_ha_state("sensor.processor_temperature")
        if cpu_temp:
            temp = float(cpu_temp['state'])
            draw_text(draw, 0, 15, f"CPU: {temp:.1f}°C")
            
            # Temperature bar (0-100°C scale)
            draw_progress_bar(draw, 60, 15, 65, 8, min(temp, 100))
            
            # Fan status based on temp
            if temp > 65:
                fan_status = "HIGH"
            elif temp > 50:
                fan_status = "MED"
            elif temp > 40:
                fan_status = "LOW"
            else:
                fan_status = "OFF"
            
            draw_text(draw, 0, 30, f"Fan: {fan_status}")
        
        # Time and date
        draw_text(draw, 0, 50, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        oled_device.display(image)
    except Exception as e:
        print(f"Temperature screen error: {e}", flush=True)

# Screen mapping
SCREEN_FUNCTIONS = {
    'system_overview': display_system_overview,
    'storage_info': display_storage_info,
    'network_stats': display_network_stats,
    'temperatures': display_temperatures
}

# Main loop
print(f"Starting display rotation with screens: {ENABLED_SCREENS}", flush=True)
screen_index = 0
screen_timer = time.time()
loop_count = 0

while True:
    try:
        if oled_device:
            # Check if it's time to switch screens
            if time.time() - screen_timer >= SCREEN_DURATION:
                screen_index = (screen_index + 1) % len(ENABLED_SCREENS)
                screen_timer = time.time()
            
            # Display current screen
            screen_name = ENABLED_SCREENS[screen_index]
            if screen_name in SCREEN_FUNCTIONS:
                SCREEN_FUNCTIONS[screen_name]()
            
        # Log status periodically
        if loop_count % 60 == 0:  # Every minute
            print(f"Display active, showing: {ENABLED_SCREENS[screen_index]}", flush=True)
        
        loop_count += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"Error in main loop: {e}", flush=True)
        time.sleep(5)
