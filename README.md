# Wifi Pentesting Raspberry PI (WP_RPI)

## General info

This repo contains a collection of python programms that can be used for Wifi-Pentesting. 
Pentesting should only be performed on networks where you are authorized to do so!
---

## Prerequisites

- **Raspberry Pi with Pi OS or Kali Linux**
- **Python 3.X**
- **aircrack-ng suite**
- **Wifi adapter with a chipset supporting monitor mode**

## Install and usage
```bash
git clone https://github.com/kalidavide/WP_RPi.git
'''

1. **Clone repository**
   
3. 

1. Run Network_scanner.py

sudo python3 network_scanner.py

The Scanner will scan for possible targets and write target information into the ./network_scans/network_info.csv File.

2. Remove all lines except for the networks you would like to attack

3. Create a custom Wordlist using the wordlist_creator.py script

sudo python3 wordlist_creator.py

4. Run the network_attacker.py to attack all networks in the network_info file

5. Any networks that were attacked will be written into the crack_results.csv file, including the key if the attack was successfull.
