"""
Name:        Network Scanner 
Version:        1.0
Author:         Lucas G. 
Description:    Scans for available wireless networks and extracts MAC and SSID information.
Date:           18.11.2024
Usage:          python3 network_scanner.py
Dependencies:   airmon-ng, airodump-ng, Python 3.x, CSV, wireless adapter supporting monitor mode

"""

import subprocess
import csv
import json

def load_config():
    with open("wpconfig.json", "r") as f:
        return json.load(f)

def scan_networks(interface, scan_output):
    subprocess.run(["airodump-ng", "-w", scan_output, "--output-format", "csv", interface], timeout=30)

def extract_mac_ssid(input_file, scan_output):
    with open(input_file, "r") as csvfile, open(scan_output, "w") as outfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 14 and row[0] != "Station MAC":
                mac, ssid = row[0].strip(), row[13].strip()
                outfile.write(f"{mac},{ssid}\n")
