## Introduction

asterisk_reconnect is a tool to periodically check that a list of clients are connected to Asterisk, and if they are not connected it will attempt to reconnect them and drop them into the specified context and extension.

## Features

* Periodically checks which clients are connected to Asterisk via the AMI.
* If a client is not connected, asterisk_reconnect will attempt to reconnect.
* Check intervals, retry intervals and clients, contexts and extensions are fully customisable.
* Works with SIP Clients. Other channel types are untested.

## Caveats

* asterisk_reconnect is designed for python 3 only!
* To date, this has only been tested on a Debian based, AllStar Asterisk (1.8) system
* It's important you secure your .cfg file, as anyone with access to the configuration can dial any client (Fraud Risk)


## Quick Install

Change to root:

    sudo su

#### Clone the repo

    cd /opt/
    git clone https://github.com/marrold/asterisk_reconnect.git

#### Install required dependancies

Change into the directory:

    cd asterisk_reconnect

Install requirements:

    pip3 install -r requirements.txt


#### Edit the configuration

Copy/Rename the sample configuration:

    cp asterisk_reconnect-sample.cfg asterisk_reconnect.cfg

Edit the defaults, use the comments as a guide:

    vim asterisk_reconnect.cfg

Check it runs:

    python3 asterisk_reconnect.py


#### Tweak Asterisk

In order for Asterisk to mark calls as down, it needs a method of detecting lack of activity on a channel. Theres two methods documented below.


##### rtptimeout

In order for this to work your 'client' will need to always send RTP, even when silent / muted / on hold etc:

Open sip.conf for editing

    vim /etc/asterisk/sip.conf

Add the following in the `[general]` section:

    rtptimeout=60

##### session-timers

If you're application intentionally stops sending RTP occasionally , you can enable session-timers to detect when a call drops. This will require a client with [RFC4028](https://tools.ietf.org/html/rfc4028) support, and detecting a dropped call will potentially take longer than the `rtptimeout` method.

Open sip.conf for editing

    vim /etc/asterisk/sip.conf

Add the following in the `[general]` section:

    session-timers=originate
    session-expires=300
    session-minse=90
    session-refresher=uac


#### Start asterisk_reconnect on boot

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


## Additional Configuration

### Logging

##### Configuration File Options

* **log_file** - Path for log file
* **log_handlers** - Comma separated list of log handlers (see below)
* **log_level** - Log Level (DEBUG / INFO / WARNING / ERROR / CRITICAL)
* **log_name** - Name of log

The following config options are optional and only apply to rotating handlers. For more information see the [documention](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler)
* **rotate_at** - When to rotate log
* **rotate_interval** - How often to rotate log
* **backup_count** - How many previous logs to store before deletion

##### Handlers

* **null** - No logging
* **console** - Print to console
* **console-timed** - Print to console with timestamp
* **file** - Write to file
* **file-timed** - Write to file with timestamp
* **file-rotate** - Write to rotating file
* **file-timed-rotate** - Write to rotating file with timestamp
* **syslog** - Write to syslog


## Licence

This project is licensed under the [Creative Commons CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) licence.

You are free to share and adapt the code as required, however you *must* give appropriate credit and indicate what changes have been made. You must also distribute your adaptation under the same license. Commercial use is prohibited.

## Acknowledgements

Thanks to everyone who contributed to the various modules utilised within this project.
