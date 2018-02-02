# iGrill
Monitor your iGrill_v2 (with a Raspberry Pi 1/2/3) - and an forward it to an mqtt-server

## What do you need
### Hardware
* iGrill2 Device (and at least one probe) - [Weber Homepage - DE](http://www.weber.com/DE/de/zubehoer/werkzeuge/-igrill/7221.html)
* A bluetooth enabled computer - preferable a raspberry pi
* A mqtt server as message receiver

### Software
* [bluepy](https://github.com/IanHarvey/bluepy)
* [paho mqtt](https://pypi.python.org/pypi/paho-mqtt/1.1)
* [pycrypto](https://pypi.python.org/pypi/pycrypto/2.6.1)

## Installation
1. clone this repo
1. install required modules
1. change the `ADDRESS` to the address of your iGrill - to find it out just run `hcitool lescan`
1. start application `python monitor_igrill_v2.py`
1. enjoy

### systemd startup-script

Place this file into the proper folder - for instance: `/lib/systemd/system/igrill.service`

```bash
[Unit]
Description=igrill MQTT service
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=2
ExecStart=/usr/bin/python /opt/igrill/monitor_igrill_v2.py

[Install]
WantedBy=multi-user.target
```

Run `systemctl daemon-reload && systemctl enable igrill && systemctl start igrill`

Next time you reboot, the iGrill service will connect and reconnect if something goes wrong...
