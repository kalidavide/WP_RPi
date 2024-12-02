# WP_RPi
 Project for scool

Usage:


1. Run Network_scanner.py

sudo python3 network_scanner.py

The Scanner will scan for possible targets and write target information into the ./network_scans/network_info.csv File.

2. Remove all lines except for the networks you would like to attack

3. Create a custom Wordlist using the wordlist_creator.py script

sudo python3 wordlist_creator.py

4. Run the network_attacker.py to attack all networks in the network_info file

5. Any networks that were attacked will be written into the crack_results.csv file, including the key if the attack was successfull.
