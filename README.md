# iGrill
Monitor your iGrill (mini, v2 or v3) (with a Raspberry Pi 1/2/3) - and forward it to a mqtt-server

## What do you need
### Hardware
* An iGrill Device (and at least one probe) - **iGrill mini**, **iGrill 2** or **iGrill 3**
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

### Docker

1. clone this repo
1. Create a folder for your config (E.g. <repo_path>/config)
1. Copy example config files from exampleconfig folder to your config folder
1. Modify example config files to match your devices and mqtt setup
1. Build Docker image: `docker build . -t igrill`
1. Run docker image, mounting the config folder: `docker run --network host --name igrill -v <path_to_config_dir>:/usr/src/igrill/config igrill`
1. Profit!

## Troubleshooting

If your device is stuck on "Authenticating" the following has been reported to work:
1. within the file /etc/bluetooth/main.conf under [Policy] check the existence of
AutoEnable=true
1. Comment out below line in /lib/udev/rules.d/90-pi-bluetooth.rules
by prefixing "#" the line ACTION=="add", SUBSYSTEM=="bluetooth", KERNEL=="hci[0-9]*", RUN+="/bin/hciconfig %k up"
