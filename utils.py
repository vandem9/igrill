from igrill import IGrillMiniPeripheral, IGrillV2Peripheral, IGrillV3Peripheral, DeviceThread
import logging
import os
import paho.mqtt.client as mqtt
import yaml
from yamlreader import yaml_load


def log_setup(log_level, logfile):
    """Setup application logging"""

    numeric_level = logging.getLevelName(log_level.upper())
    if not isinstance(numeric_level, int):
        raise TypeError('Invalid log level: {0}'.format(log_level))

    if logfile is not '':
        logging.info('Logging redirected to: ' + logfile)
        # Need to replace the current handler on the root logger:
        file_handler = logging.FileHandler(logfile, 'a')
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for handler in log.handlers:  # remove all old handlers
            log.removeHandler(handler)
        log.addHandler(file_handler)

    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

    logging.getLogger().setLevel(numeric_level)
    logging.info('log_level set to: {0}'.format(log_level))


def mqtt_init(mqtt_config):
    """Setup mqtt connection"""
    mqtt_client = mqtt.Client()

    if 'auth' in mqtt_config:
        auth = strip_config(mqtt_config['auth'], ['username', 'password'])
        mqtt_client.username_pw_set(**auth)

    if 'tls' in mqtt_config:
        if mqtt_config['tls']:
            tls_config = strip_config(mqtt_config['tls'], ['ca_certs', 'certfile', 'keyfile', 'cert_reqs', 'tls_version'])
            mqtt_client.tls_set(**tls_config)
        else:
            mqtt_client.tls_set()

    mqtt_client.connect(**strip_config(mqtt_config, ['host', 'port', 'keepalive']))
    return mqtt_client


def publish(temperatures, battery, client, base_topic, device_name):
    for i in range(1,5):
        if temperatures[i]:
            client.publish("{0}/{1}/probe{2}".format(base_topic, device_name, i), temperatures[i])

    client.publish("{0}/{1}/battery".format(base_topic, device_name), battery)


def get_devices(device_config):
    if device_config is None:
        logging.warn("No devices in config")
        return {}

    device_types = {'igrill_mini': IGrillMiniPeripheral,
                    'igrill_v2': IGrillV2Peripheral,
                    'igrill_v3': IGrillV3Peripheral}

    return [device_types[d['type']](**strip_config(d, ['address', 'name'])) for d in device_config]


def get_device_threads(device_config, mqtt_client):
    if device_config is None:
        logging.warn("No devices in config")
        return {}

    return [DeviceThread(ind, d['name'], d['address'], d['type'], mqtt_client, d['topic'], d['interval']) for ind, d in enumerate(device_config)]


def read_config(config_path):
    """Read config file from given location, and parse properties"""
    if not os.path.isdir(config_path):
        raise ValueError('{0} is not a directory'.format(config_path))

    defaultconfig = {
        "mqtt": {
            "host":         "localhost"
        }
    }

    try:
        return yaml_load(config_path, defaultconfig)
    except yaml.YAMLError:
        logging.exception('Failed to parse configuration directory:')


def strip_config(config, allowed_keys):
    return {k: v for k, v in config.iteritems() if k in allowed_keys and v}
