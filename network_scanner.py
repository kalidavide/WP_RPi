"""
Name:           Network Scanner 
Version:        1.2
Author:         Lucas G. 
Description:    Scans for available wireless networks and extracts network information
Date:           9.12.2024
Usage:          python3 network_scanner.py
Dependencies:   aircrack-ng, Python 3.x, CSV, wireless adapter supporting monitor mode
"""
#Load modules
import subprocess, csv, os, time, json, glob 

def load_config(config_file="wpconfig.json"):
    """
    Loads central config file

    - Load config file
    - Error handling
    """
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{config_file}' not found.")
        exit(1)

def setup_output(output_dir):
    """
    Creates output directory for NW Scans

    - Check for output directory
    - If not existing, create output directory
    - Error handling 
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[INFO] Created directory: {output_dir}")
    else:
        print(f"[INFO] Using existing directory: {output_dir}")

def rfkill_unblock():
    """
    Unblocks (potentially) disabled Wifi Hardware

    - Unblock all wifi adapters
    - Error handling
    """
    try:
        os.system("rfkill unblock wifi")
        print("[INFO] Wifi is unblocked")
    except Exception as e:
        print(f"[ERROR] Something went wrong, wifi still blocked: {e}")

def enable_monitormode(interface):
    """
    Enable monitor mode via interface settings

    - Stop interface
    - Set monitor mode
    - Start interface
    - Error handling
    """
    print("[INFO] Enabling monitor mode...")
    try:
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)
        subprocess.run(["iw", "dev", interface, "set", "type", "monitor"], check=True)
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        print(f"[INFO] {interface} is now in monitor mode.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to enable monitor mode: {e}")
        exit(1)

def enable_managedmode(interface):
    """
    enable managed mode via interface settings

    - Stop interface
    - Set managed mode
    - Start interface
    - Error handling
    """
    print("[INFO] Enabling managed mode...")
    try:
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)
        subprocess.run(["iw", "dev", interface, "set", "type", "managed"], check=True)
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        print(f"[INFO] {interface} is back to managed mode.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to enable managed mode: {e}")
        exit(1)

def scan_networks(interface, scan_prefix, duration):
    """
    Scan networks using airodump-ng

    - Scan nearby networks, writing output into scan direcotry
    - Run scan for duration set in config file
    - Error handling
    """
    print(f"[INFO] Scanning for networks on {interface} for {duration} seconds...")
    try:
        scan_command = [
            "airodump-ng",
            "-w", scan_prefix,
            "--output-format", "csv",
            interface
        ]
        process = subprocess.Popen(scan_command)
        time.sleep(duration)
        process.terminate()
        print("[INFO] Network scan completed.")
    except Exception as e:
        print(f"[ERROR] Failed to scan networks: {e}")

def extract_networkinfo(csv_file, output_file):
    """
    Extract network info from scans into dedicated File

    - Reads scan
    - Creates new file with only MAC, SSID, Channel &Singal
    - Extracts all relevant info from scan file and writes into new file
    - Error handling
    """
    try:
        print(f"[INFO] Extracting network data from {csv_file}...")
        with open(csv_file, "r") as infile, open(output_file, "w") as outfile:
            reader = csv.reader(infile)
            outfile.write("MAC,SSID,Channel,Signal\n")  
            for row in reader:
                if len(row) > 14 and row[0].strip() != "BSSID":
                    mac, ssid = row[0].strip(), row[13].strip()
                    channel, signal = row[3].strip(), row[8].strip()
                    outfile.write(f"{mac},{ssid},{channel},{signal}\n")
        print(f"[INFO] Network data saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to extract network info: {e}")

def main():
    """
    Main function to call functions and read from latest network scan

    - Call 'load_config' function and define variables
    - Call 'setup_output' function
    - Set naming for network scans and network info
    - Call 'rfkill_unblock', 'enable_monitormode' & 'scan_networks' functions
    - Dynamically detec network_scan with the highest number to use latest scan
    - Error handling
    """

    config = load_config()
    interface = config.get("interface")
    output_dir = config.get("scan_dir")
    scan_duration = config.get("scan_duration")

    setup_output(output_dir)
    
    scan_prefix = os.path.join(output_dir, "network_scan")
    network_info = os.path.join(output_dir, "network_info.csv")
    
    try:
        rfkill_unblock()
        enable_monitormode(interface)
        scan_networks(interface, scan_prefix, scan_duration)

        csv_files = [
            file for file in os.listdir(output_dir) 
                if file.startswith("network_scan") 
        ]
        if csv_files:
            csv_file = max(
                csv_files,
                key=lambda f: int(f.split("-")[-1].split(".csv")[0])  
            )
            csv_file = os.path.join(output_dir, csv_file) 
            extract_networkinfo(csv_file, network_info)
        else:
            print(f"[ERROR] No scan files found with prefix {scan_prefix}.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        enable_managedmode(interface)

if __name__ == "__main__":
    main()
