#!/usr/bin/env python

import argparse
import logging
import threading
import time

from utils import read_config, log_setup, mqtt_init, get_device_threads


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

    # Connect to MQTT
    client = mqtt_init(config['mqtt'])

    run_event = threading.Event()
    run_event.set()
    # Get device threads
    devices = get_device_threads(config['devices'], client, run_event)

    for device in devices:
        device.start()

    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        logging.info("Signaling all device threads to finish")

        run_event.clear()
        for device in devices:
            device.join()

        logging.info("All threads finished, exiting")


if __name__ == '__main__':
    main()