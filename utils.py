from builtins import range
from config import strip_config
from config import Config
import argparse
from igrill import IGrillMiniPeripheral, IGrillV2Peripheral, IGrillV3Peripheral, Pulse2000Peripheral, DeviceThread
import logging
import paho.mqtt.client as mqtt
import boto3
import time

config_requirements = {
    'specs': {
        'required_entries': {'devices': list, 'mqtt': dict},
    },
    'children': {
        'devices': {
            'specs': {
                'required_entries': {'name': str, 'type': str, 'address': str, 'topic': str, 'interval': int},
                'optional_entries': {'publish_missing_probes': bool, 'missing_probe_value': str},
                'list_type': dict
            }
        },
        'mqtt': {
            'specs': {
                'required_entries': {'host': str,
                                     'aws_cloudwatch_metrics': bool},
                'optional_entries': {'port': int,
                                     'keepalive': int,
                                     'auth': dict,
                                     'tls': dict}
            },
            'children': {
                'auth': {
                    'specs': {
                        'required_entries': {'username': str},
                        'optional_entries': {'password': str}
                    }
                },
                'tls': {
                    'specs': {
                        'optional_entries': {'ca_certs': str,
                                             'certfile': str,
                                             'keyfile': str,
                                             'cert_reqs': str,
                                             'tls_version': str,
                                             'ciphers': str}
                    }
                }
            }
        }
    }
}

config_defaults = {
    'mqtt': {
        'host': 'localhost'
    }
}

parser = argparse.ArgumentParser(description='Monitor bluetooth igrill devices, and export to MQTT')
parser.add_argument('-c', '--config', action='store', dest='config_directory', default='.',
                    help='Set config directory, default: \'.\'')
parser.add_argument('-l', '--log-level', action='store', dest='log_level', default='INFO',
                    help='Set log level, default: \'info\'')
parser.add_argument('-d', '--log-destination', action='store', dest='log_destination', default='',
                    help='Set log destination (file), default: \'\' (stdout)')
parser.add_argument('--configtest', help='Parse config only',
                    action="store_true")
options = parser.parse_args()


def log_setup(log_level, logfile):
    """Setup application logging"""

    numeric_level = logging.getLevelName(log_level.upper())
    if not isinstance(numeric_level, int):
        raise TypeError("Invalid log level: {0}".format(log_level))

    if logfile != '':
        logging.info("Logging redirected to: ".format(logfile))
        # Need to replace the current handler on the root logger:
        file_handler = logging.FileHandler(logfile, 'a')
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for handler in log.handlers:  # remove all old handlers
            log.removeHandler(handler)
        log.addHandler(file_handler)

    else:
        logging.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s: %(message)s')

    logging.getLogger().setLevel(numeric_level)
    logging.info("log_level set to: {0}".format(log_level))


def mqtt_init(mqtt_config):
    """Setup mqtt connection"""
    mqtt_client = mqtt.Client()

    if 'auth' in mqtt_config:
        auth = mqtt_config['auth']
        mqtt_client.username_pw_set(**auth)

    if 'tls' in mqtt_config:
        if mqtt_config['tls']:
            tls_config = mqtt_config['tls']
            mqtt_client.tls_set(**tls_config)
        else:
            mqtt_client.tls_set()

    mqtt_client.connect(**strip_config(mqtt_config, ['host', 'port', 'keepalive']))
    return mqtt_client

def putMetricData(metricName, value, currentTimestamp):
    cwClient = boto3.client('cloudwatch')
    response = cwClient.put_metric_data(
        Namespace='iGrill',
        MetricData=[
            {
                'MetricName': metricName,
                'Timestamp': currentTimestamp,
                'Value': value
            }
        ]
    )

def publish(temperatures, battery, heating_element, client, base_topic, device_name):
    aws_options = parser.parse_args()
    aws_config = Config(aws_options.config_directory, config_requirements, config_defaults)
    aws_mqtt_config = aws_config.get_config('mqtt')

    if 'aws_cloudwatch_metrics' in aws_mqtt_config and aws_mqtt_config['aws_cloudwatch_metrics'] == True:
        logging.debug("using aws cloudwatch metrics")
        currentTimestamp = time.time()

        for i in range(1, 5):
            if temperatures[i]:
                putMetricData("probe" + str(i), temperatures[i], currentTimestamp)
        if battery:
            putMetricData("battery", battery, currentTimestamp)

    else:
        logging.debug("using legacy mqtt")
        for i in range(1, 5):
            if temperatures[i]:
                client.publish("{0}/{1}/probe{2}".format(base_topic, device_name, i), temperatures[i])

        if battery:
            client.publish("{0}/{1}/battery".format(base_topic, device_name), battery)
        if heating_element:
            client.publish("{0}/{1}/heating_element".format(base_topic, device_name), heating_element)


def get_devices(device_config):
    if device_config is None:
        logging.warn('No devices in config')
        return {}

    device_types = {'igrill_mini': IGrillMiniPeripheral,
                    'igrill_v2': IGrillV2Peripheral,
                    'igrill_v3': IGrillV3Peripheral,
                    'pulse_2000': Pulse2000Peripheral}

    return [device_types[d['type']](**strip_config(d, ['address', 'name'])) for d in device_config]


def get_device_threads(device_config, mqtt_config, run_event):
    if device_config is None:
        logging.warn('No devices in config')
        return {}

    return [DeviceThread(ind, mqtt_config, run_event, **d) for ind, d in
            enumerate(device_config)]
