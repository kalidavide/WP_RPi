# Wifi Pentesting Raspberry PI (WP_RPI) [Proof of Concept]

## General info

This repo contains a collection of python programms that can be used for Wifi-Pentesting. 
Pentesting should only be performed on networks where you are authorized to do so!

Project for school by Davide B. & Lucas G.

---

## Prerequisites

- **Raspberry Pi with Pi OS or Kali Linux**
- **Python 3.X**
- **aircrack-ng suite**
- **Wifi adapter with a chipset supporting monitor mode**

## Install and usage

1. **Clone repository**
```bash
git clone https://github.com/kalidavide/WP_RPi.git
cd WP_RPI
```

2. **Set configuration parameter**
   
   Edit the wpconfig.json with your editor of choice and change the configuration variables as needed
   
4.  **Run network scanner**

   The scanner will set your defined wifi adapter to monitor mode and scan for available networks in the area, all results will be writted into the network_scan-0X.csv and network_info.csv files.
```bash
sudo python3 network_scanner.py
```

   
4.  **Check the network_scans folder**

   The network_scans folder should now contain a network_scan-0X.csv and a network_info.csv file. 
   **Attention**
   All networks listed in the network_info.csv file will be used as targets by the network attacker, remove any that you don't want to attack before running the attacker.

4.  **Create a wordlist to perform the attack**
```bash
sudo python3 wordlist_creator.py
```
You can also use a custom wordlist, just make sure the wordlist directory exists and the name of the used wordlist is defined in the wpconfig.json
   
6.  **Run network attacker**

   The script will attempt to capture a handshake and then brute force the key using all entires of the wordlist. 
```bash
sudo python3 network_attacker.py
```
   The results of successful or unsuccessful attempts will be written in the crack_results.csv file.





