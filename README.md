# ubuntu-systemlink-salt-minion

### 1.  Install Ubuntu 18.04
Ubuntu 18.04 comes with Python 3.6.8 installed by default.

### 2.  Clone or download this repo to the Ubuntu OS
After downloading the .zip or cloning the repo, the remainder of the commands should reference the files inside the path where you extracted the files.

### 3.  Add the current SaltStack repository to the system
```wget -O - https://repo.saltstack.com/apt/debian/9/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add -```

```touch /etc/apt/sources.list.d/saltstack.list```

Set ```deb http://repo.saltstack.com/apt/debian/9/amd64/latest stretch main``` as the contents of ```/etc/apt/sources.list.d/saltstack.list```

These steps were based on those from SaltStack directly:
https://repo.saltstack.com/#debian

The version of salt-minion in the Ubuntu 18.04 distribution is quite old (2017.7.4) and needs to be updated to a more recent version.  This adds the new feed to the aptitude package manager and installs the public key for that repo.  We define the URL to the repo in the saltstack.list.  This URL pins the verion to the latest repo, but it could be modified to point to a specific version if needed.  See the SaltStack documentation for more information.

### 4.  Update the package repository based on the newly added feeds
```suddo apt-get update```

This ensures we're installing the latest packages from the feeds.

### 5.  Install python3-pip
```sudo apt-get install python3-pip```

This will be used in the next step to install the SystemLink python SDK
### 6.  Install SystemLink python SDK
```pip3 install ./systemlink_sdk-19.5.0-py3-none-any.whl```

This automatically installs the python libraries for communicating with the SystemLink server.  Pip3 will auto-detect the currently active version of python and install the python modules into the correct directories to be detected and imported by your code.
### 7.  Install Salt Minion
```sudo apt-get install salt-minion```

At the time of creation, this installs the latest salt-minion (2019.2.0 Flourine).

### 8.  Stop the salt-minion service
```/etc/init.d/salt-minion stop```

Stop the salt minion service so that python libraries and configuration files can be modified without having it try to connect during modification.
### 9.  Copy extmods from LinuxRT system onto Ubuntu system
```mkdir /var/lib/salt```

```mkdir /var/lib/salt/minion```

```mkdir /var/lib/salt/minion/extmods```

```cp -r ./var/lib/salt/minion/extmods/* /var/lib/salt/minion/extmods/```

This contains SystemLink specific modules, grains, and beacons that customize how the salt-minion behaves.
### 10.  Set minion id
Edit ```/etc/salt/minion_id``` and set the identifier that you want to show up in SystemLink's Systems Management UI.  This should be a unique value that avoids special characters.  Use hyphens instead of underscores.
### 11.  Set the salt master host
Edit ```/etc/salt/minion.d/master.conf``` to point to your SystemLink server.  This can be a fully-qualified domain name, hostname, or IP address as long as that resolves on your network.
### 12.  Copy systemlink.conf to /etc/salt/minion.d
```cp ./etc/salt/minion.d/systemlink.conf /etc/salt/minion.d/```

This configuration file sets some default behavior of the minion modules and specific file paths where to put / find files.
### 13.  Delete the master public key
```rm -rf /var/lib/salt/pki/minion/minion_master.pub```

The master's public key will be wrong if you've ever connected to a different salt-master before.  Since it may automatically try to connect to a server when the salt-minion starts after installation, you may need to delete this to prevent mismatched master keys.  It will obtain a new key from the master when it connects the next time.
### 14.  Restart the salt-minion
```/etc/init.d/salt-minion restart```

Now that we've customized the salt-minion modules, we need to restart the service for them to take effect.

### 15.  Approve the minion in the SystemLink Systems Management UI
The minion's security key now needs to be approved by the SystemLink server to allow the minion to connect.
Modify the URL below to point to the SystemLink Server instead of localhost:

http://localhost/#systemsmanagement/unapproved

Verify the key is correct and click the 'Approve' button next to the minion you want to allow to connect.

### Verification
Verify that ```/etc/natinst/niskyline/HttpConfigurations/http_master.json``` exists.  If the minion has successfully connected to the master, it will have automatically and securely transferred the HTTP connection information (including a generated API key) to the minion which the python SDK will use to connect.

There will still be errors in the salt minion log about 'NoneType for grains is not subscriptable'.  This is OK.

