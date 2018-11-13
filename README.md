# SousPi
A web application that runs on a Raspberry Pi and connects to an Anova Precision Cooker to facilitate starting/stopping 
the device whenever you like.

# Requirements
- Raspberry Pi or some other Linux-based environment with Bluetooth available
- Python 2.7
- BluePy

# Setup
    # clone the git repo
    $ git clone https://github.com/blbuford/souspi
    $ cd souspi
    $ python setup.py sdist
    
    # Copy the files from your local machine to the remote host. 
    # Adjust user@host:path to your specifics!
    $ scp dist/souspi-0.0.1.tar.gz pi@rpi.local:/tmp/
    $ ssh pi@rpi.local
    
    # Extract the tarball to the home directory (~)
    $ tar -xzvf /tmp/souspi-0.0.1.tar.gz
    $ cd souspi-0.0.1
    $ pip install -r requirements.txt
    
    # The enviroment is now setup. Now all that's left is discovering your device's MAC address.
    # The anova_scanner.py script will output the MAC addresses of all Anova devices that it can see.
    # It must be run with sudo to be able to scan!
    $ sudo python anova_scanner.py
    'Anova', MAC: 78:a5:04:29:1a:3d
    
    # Copy and paste your MAC address into the config/web.conf file for the variable ANOVA_MAC_ADDRESS
    # You're done! Run the run.py script.
    $ python run.py

Enjoy!

# Thanks to...
- @IanHarvey for BluePy (https://github.com/IanHarvey/bluepy)