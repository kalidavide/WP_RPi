"""
Name:           Network Scanner 
Version:        1.1
Author:         Lucas G. 
Description:    Scans for available wireless networks and extracts network information.
Date:           30.11.2024
Usage:          python3 network_scanner.py
Dependencies:   airmon-ng, airodump-ng, Python 3.x, CSV, wireless adapter supporting monitor mode
"""
#Load modules
import subprocess, csv, os, time, json

def load_config(config_file="wpconfig.json"):
    """Load config"""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{config_file}' not found.")
        exit(1)

def setup_output(output_dir):
    """Ensure output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[INFO] Created directory: {output_dir}")
    else:
        print(f"[INFO] Using existing directory: {output_dir}")

def rfkill_unblock_wifi():
    """Unblock WLAN adapter"""
    try:
        os.system("rfkill unblock wifi")
        print("[INFO] wifi is unblocked")
    except Exception as e:
        print(f"[ERROR] Something went wrong, wifi still blocked: {e}")

def rfkill_block_wifi():
    """Block WLAN adapter"""
    try:
        os.system("rfkill block wifi")
        print("[INFO] wifi is blocked")
    except Exception as e:
        print(f"[ERROR] Something went wrong, wifi still unblocked: {e}")

def enable_monitor_mode(interface):
    """Enable monitor mode"""
    print("[INFO] Enabling monitor mode...")
    try:
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)
        subprocess.run(["iw", "dev", interface, "set", "type", "monitor"], check=True)
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        print(f"[INFO] {interface} is now in monitor mode.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to enable monitor mode: {e}")
        exit(1)

def disable_monitor_mode(interface):
    """Disable monitor mode"""
    print("[INFO] Disabling monitor mode...")
    try:
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)
        subprocess.run(["iw", "dev", interface, "set", "type", "managed"], check=True)
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        print(f"[INFO] {interface} is back to managed mode.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to disable monitor mode: {e}")
        exit(1)

def scan_networks(interface, output_prefix, duration):
    """airodump-ng to scan networks."""
    print(f"[INFO] Scanning for networks on {interface} for {duration} seconds...")
    try:
        scan_command = [
            "airodump-ng",
            "-w", output_prefix,
            "--output-format", "csv",
            interface
        ]
        process = subprocess.Popen(scan_command)
        time.sleep(duration)
        process.terminate()
        print("[INFO] Network scan completed.")
    except Exception as e:
        print(f"[ERROR] Failed to scan networks: {e}")

def extract_network_info(csv_file, output_file):
    """Extract network information"""
    try:
        print(f"[INFO] Extracting network data from {csv_file}...")
        with open(csv_file, "r") as infile, open(output_file, "w") as outfile:
            reader = csv.reader(infile)
            outfile.write("MAC,SSID,Channel,Signal\n")  # Header row
            for row in reader:
                if len(row) > 14 and row[0].strip() != "BSSID":
                    mac, ssid = row[0].strip(), row[13].strip()
                    channel, signal = row[3].strip(), row[8].strip()
                    outfile.write(f"{mac},{ssid},{channel},{signal}\n")
        print(f"[INFO] Network data saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to extract network info: {e}")

def main():
    """Main function to execute the scanning workflow."""
    config = load_config()
    
    interface = config.get("interface")
    output_dir = config.get("scan_dir")
    scan_duration = config.get("scan_duration")

    setup_output(output_dir)
    
    scan_output_prefix = os.path.join(output_dir, "scanned_networks")
    network_info_file = os.path.join(output_dir, "network_info.csv")
    
    try:
        rfkill_unblock_wifi()
        enable_monitor_mode(interface)
        scan_networks(interface, scan_output_prefix, scan_duration)
        csv_file = scan_output_prefix + "-01.csv"  
        if os.path.exists(csv_file):
            extract_network_info(csv_file, network_info_file)
        else:
            print(f"[ERROR] Expected scan file {csv_file} not found.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        disable_monitor_mode(interface)
        rfkill_block_wifi()

if __name__ == "__main__":
    main()
