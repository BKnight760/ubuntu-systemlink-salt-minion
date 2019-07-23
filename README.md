# ubuntu-systemlink-salt-minion

### 1.  Install Ubuntu 18.04
Ubuntu 18.04 comes with Python 3.6.8 installed by default.
### 2.  Install python3-pip
```sudo apt-get install python3-pip```
This will be used in the next step to install the SystemLink python SDK
### 3.  Install SystemLink python SDK
```pip3 install ~/Desktop/systemlink_sdk-19.5.0-py3-none-any.whl```
This automatically installs the python libraries for communicating with the SystemLink server.  Pip3 will auto-detect the currently active version of python and install the python modules into the correct directories to be detected and imported by your code.
### 4.  Install Salt Minion
```sudo apt-get install salt-minion```
At the time of creation, this installes the Salt Minion version 2017.7.4+dfsg1-1ubuntu18.04.1.  This is not the same version as what is installed on NI Linux RT, and so we'll have to modify a few files to get it to work.
### 5.  Set minion id
Edit ```/etc/salt/minion_id``` and set the identifier that you want to show up in SystemLink's Systems Management UI.  This should be a unique value that avoids special characters.  Use hyphens instead of underscores.
### 6.  Set the salt master host
Edit ```/etc/salt/minion.d/master.conf``` to point to your SystemLink server.  This can be a fully-qualified domain name, hostname, or IP address as long as that resolves on your network.
### 7.  Copy systemlink.conf to /etc/salt/minion.d
```cp ~/Desktop/salt/systemlink.conf /etc/salt/minion.d/```
This configuration file sets some default behavior of the minion modules and specific file paths where to put / find files.
### 8.  Delete the master public key
```rm -rf /var/lib/salt/pki/minion/minion_master.pub```
The master's public key will be wrong if you've ever connected to a different salt-master before.  Since it may automatically try to connect to a server when the salt-minion starts after installation, you may need to delete this to prevent mismatched master keys.
### 9.  Copy extmods from LinuxRT system onto Ubuntu system
```cp -r ~/Desktop/extmods/ /var/lib/salt/minion/extmods/```
This contains SystemLink specific modules, grains, and beacons that customize how the salt-minion behaves.
### 10.  Override some of the salt utilities
```cp ~/Desktop/salt/utils/data.py /usr/lib/python3/dist-packages/salt/utils/```
```cp ~/Desktop/salt/utils/platform.py /usr/lib/python3/dist-packages/salt/utils/```
```cp ~/Desktop/salt/utils/stringutils.py /usr/lib/python3/dist-packages/salt/utils/```
```cp ~/Desktop/salt/utils/files.py /usr/lib/python3/dist-packages/salt/utils/```
```cp -r ~/Desktop/salt/utils/decorators/jinja.py /usr/lib/python3/dist-packages/salt/utils/decorators/```

The salt-minion installed for Ubuntu 18.04 is not compatible with some of the NI Linux RT modules.  We'll replace a couple of these files to make it work.  It looks like recent versions of salt-minion's directory structure have been modified so these files exist in different locations than where the modules knew where they were previously.

### 11.  Restart the salt-minion
```/etc/init.d/salt-minion restart```
Now that we've customized the salt-minion python code and the modules, we need to restar the service.

### Verification
Verify that /etc/natinst/niskyline/HttpConfigurations/http_master.json exists.

There will still be errors in the salt minion log about NoneType for grains is not subscriptable.  This is OK.

