# ubuntu-systemlink-salt-minion

### 1.  Install Ubuntu 18.04
Ubuntu 18.04 comes with Python 3.6.8 installed by default.

### 2.  Clone or download this repo to the Ubuntu OS
After downloading the .zip or cloning the repo, the remainder of the commands should reference the files inside the path where you extracted the files.

### 3.  Install python3-pip
```suddo apt-get update```

```sudo apt-get install python3-pip```

This will be used in the next step to install the SystemLink python SDK
### 4.  Install SystemLink python SDK
```pip3 install ./systemlink_sdk-19.5.0-py3-none-any.whl```

This automatically installs the python libraries for communicating with the SystemLink server.  Pip3 will auto-detect the currently active version of python and install the python modules into the correct directories to be detected and imported by your code.
### 5.  Install Salt Minion
```sudo apt-get install salt-minion```

At the time of creation, this installes the Salt Minion version 2017.7.4+dfsg1-1ubuntu18.04.1.  This is not the same version as what is installed on NI Linux RT, and so we'll have to modify a few files to get it to work.
### 6.  Stop the salt-minion service
```/etc/init.d/salt-minion stop```

Stop the salt minion service so that python libraries and configuration files can be modified without having it try to connect during modification.
### 7.  Copy extmods from LinuxRT system onto Ubuntu system
```mkdir /var/lib/salt/minion```

```mkdir /var/lib/salt/minion/extmods```

```cp -r ./var/lib/salt/minion/extmods/* /var/lib/salt/minion/extmods/```

This contains SystemLink specific modules, grains, and beacons that customize how the salt-minion behaves.
### 8.  Override some of the salt utilities
```cp -r ./usr/lib/python3/dist-packages/salt/utils/* /usr/lib/python3/dist-packages/salt/utils/```

The salt-minion installed for Ubuntu 18.04 is not compatible with some of the NI Linux RT modules.  We'll replace a couple of these files to make it work.  It looks like recent versions of salt-minion's directory structure have been modified so these files exist in different locations than where the modules knew where they were previously.
### 9.  Set minion id
Edit ```/etc/salt/minion_id``` and set the identifier that you want to show up in SystemLink's Systems Management UI.  This should be a unique value that avoids special characters.  Use hyphens instead of underscores.
### 10.  Set the salt master host
Edit ```/etc/salt/minion.d/master.conf``` to point to your SystemLink server.  This can be a fully-qualified domain name, hostname, or IP address as long as that resolves on your network.
### 11.  Copy systemlink.conf to /etc/salt/minion.d
```cp ./systemlink.conf /etc/salt/minion.d/```

This configuration file sets some default behavior of the minion modules and specific file paths where to put / find files.
### 12.  Delete the master public key
```rm -rf /var/lib/salt/pki/minion/minion_master.pub```

The master's public key will be wrong if you've ever connected to a different salt-master before.  Since it may automatically try to connect to a server when the salt-minion starts after installation, you may need to delete this to prevent mismatched master keys.
### 13.  Restart the salt-minion
```/etc/init.d/salt-minion restart```

Now that we've customized the salt-minion python code and the modules, we need to restar the service.

### Verification
Verify that ```/etc/natinst/niskyline/HttpConfigurations/http_master.json``` exists.

There will still be errors in the salt minion log about NoneType for grains is not subscriptable.  This is OK.

