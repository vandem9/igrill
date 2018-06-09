#!/usr/bin/env python

import argparse
import time

from utils import read_config, get_devices, log_setup, mqtt_init, publish


def main():
    # Setup argument parsing
    parser = argparse.ArgumentParser(description='Monitor bluetooth igrill devices, and export to MQTT')
    parser.add_argument('-c', '--config', action='store', dest='config_directory', default='.',
                        help='Set config directory, default: \'.\'')
    parser.add_argument('-l', '--log-level', action='store', dest='log_level', default='INFO',
                        help='Set log level, default: \'info\'')
    parser.add_argument('-d', '--log-destination', action='store', dest='log_destination', default='',
                        help='Set log destination (file), default: \'\' (stdout)')
    options = parser.parse_args()
    config = read_config(options.config_directory)

    # Setup logging
    log_setup(options.log_level, options.log_destination)

    # Get device list
    devices = get_devices(config['devices'])

    # Connect to MQTT
    client = mqtt_init(config['mqtt'])
    base_topic = config['mqtt']['base_topic']

    polling_interval = config['interval'] if 'interval' in config else 15

    while True:
        for device in devices:
            publish(device.read_temperature(), device.read_battery(), client, base_topic, device.name)

        time.sleep(polling_interval)


if __name__ == '__main__':
    main()