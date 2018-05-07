### Introduction

asterisk_reconnect is a tool to periodically check that a list of clients are connected to Asterisk, and if they are not connected it will attempt to reconnect them and drop them into the specified context and extension.

### Features

* Periodically checks which clients are connected to Asterisk via the AMI. 
* If a client is not connected, asterisk_reconnect will attempt to reconnect.
* Check intervals, retry intervals and clients, contexts and extensions are fully customisable.

### Caveats

* asterisk_reconnect is designed for python 3 only!
* To date, this has only been tested on a Debian based, AllStar Asterisk (1.8) system
* It's important you secure your .cfg file, as anyone with access to the configuration can dial any client (Fraud Risk)

### Installation

Change to root:

    sudo su
   
##### Clone the repo

    cd /opt/
    git clone [repo URL]

##### Install required dependancies


Change into the directory:

    cd asterisk_reconnect

Install requirements:

    pip3 install -r requirements.txt
    
    
##### Edit the configuration


Copy/Rename the sample configuration:

    cp asterisk_reconnect-sample.cfg asterisk_reconnect.cfg
    
Edit the defaults, use the comments as a guide:

    vim asterisk_reconnect.cfg
    
Check it runs:

    python3 asterisk_reconnect.py


##### Start asterisk_reconnect on boot

The following assumes you're using a systemd based OS such as Debian 9.

Create a systemd service file:

    vim /lib/systemd/system/asterisk_reconnect.service

Enter the following:

    [Unit]
    Description=asterisk_reconnect service
    After=syslog.target network.target
    
    [Service]
    User=root
    WorkingDirectory=/opt/asterisk_reconnect
    ExecStart=/usr/bin/python3 /opt/asterisk_reconnect/asterisk_reconnect.py
    
    [Install]
    WantedBy=multi-user.target
    
Make it executable:

    chmod 755 /lib/systemd/system/asterisk_reconnect.service

Reload the systemctl daemon:

    systemctl daemon-reload
    
Enable the service:
    
    systemctl enable asterisk_reconnect.service
    
    
### Licence

This project is licensed under the [Creative Commons CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) licence.

You are free to share and adapt the code as required, however you *must* give appropriate credit and indicate what changes have been made. You must also distribute your adaptation under the same license. Commercial use is prohibited.

### Acknowledgments

Thanks to everyone who contributed to the various modules utilised within this project.