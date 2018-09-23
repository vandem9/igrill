# iGrill
Monitor your iGrill (mini, v2 or v3) (with a Raspberry Pi 1/2/3) - and an forward it to an mqtt-server

## What do you need
### Hardware
* An iGrill Device (and at least one probe) - [iGrill mini](https://www.weber.com/US/en/accessories/cooking/igrill-and-thermometers/7202.html?cgid=1339#start=1), [iGrill v2](https://www.weber.com/US/en/accessories/cooking/igrill-and-thermometers/7203.html?cgid=1339#start=1) or [igrill v3](https://www.weber.com/US/en/accessories/cooking/igrill-and-thermometers/7204.html?cgid=1339#start=1)
* A bluetooth enabled computer - preferable a raspberry pi
* A mqtt server as message receiver

## Installation
1. clone this repo
1. install required modules (see requirements.txt)
1. Add at least one device config (see ./exampleconfig/device.yaml) - to find your device MAC just run `hcitool lescan`
1. start application `./monitor.py`
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
ExecStart=/usr/bin/python <path_to_igrill_repo>/monitor.py -c <path_to_config_dir>

[Install]
WantedBy=multi-user.target
```

Run `systemctl daemon-reload && systemctl enable igrill && systemctl start igrill`

Next time you reboot, the iGrill service will connect and reconnect if something goes wrong...
