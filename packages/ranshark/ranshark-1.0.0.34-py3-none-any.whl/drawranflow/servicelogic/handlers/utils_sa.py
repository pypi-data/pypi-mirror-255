import logging
from django.conf import settings
import os
import json
import pandas as pd
import numpy as np
import logging


def get_tmsi(input_string):
    if input_string is not np.nan:

        # Remove the ':' delimiter
        input_string = input_string.replace(':', '')

        # Consider only first NRCELL the ':' delimiter
        input_string = input_string.split(',')[0]

        # Convert the string to an integer (assuming it's a hex number)
        int_num = int(input_string, 16)

        # Convert the result to binary
        binary_num = format(int_num, 'b')

        # Extract the first 19 bits
        first_19_bits = binary_num[:-1]

        # Convert the first 19 bits to decimal
        decimal_num = int(first_19_bits, 2)

        return decimal_num
    else:
        return np.nan


def get_trgt_gnb_id(input_string):
    # Remove the ':' delimiter
    if input_string is not np.nan:
        input_string = input_string[-8:]
        # Convert the string to an integer (assuming it's a hex number)
        int_num = int(input_string, 16)

        # Convert the result to binary
        binary_num = format(int_num, 'b')

        # Extract the first 19 bits
        first_19_bits = binary_num[:-12]
        last_12_bits = binary_num[-12:]

        # Convert the first 19 bits to decimal
        decimal_num_gnb = int(first_19_bits, 2)
        decimal_num_lcd = int(last_12_bits, 2)
        # print(decimal_num_lcd,decimal_num_gnb)
        return str(decimal_num_gnb), decimal_num_lcd if decimal_num_lcd else np.nan
    else:
        return np.nan, np.nan


def get_gnb_id(input_string):
    if input_string is not np.nan:
        # Remove the ':' delimiter

        input_string = input_string.replace(':', '')

        # Consider only first NRCELL the ':' delimiter
        input_string = input_string.split(',')[0]

        input_string = input_string[:-1]

        # Convert the string to an integer (assuming it's a hex number)
        int_num = int(input_string, 16)

        # Right shift by 4 bits (equivalent to removing 4 LSB)

        # Convert the result to binary
        binary_num = format(int_num, 'b')

        # Extract the first 19 bits
        first_19_bits = binary_num[:-12]
        last_12_bits = binary_num[-12:]

        # Convert the first 19 bits to decimal
        decimal_num_gnb = int(first_19_bits, 2)
        decimal_num_lcid = int(last_12_bits, 2)
        return decimal_num_gnb,decimal_num_lcid if decimal_num_lcid else np.nan
    else:
        return np.nan,np.nan


def open_file(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return f"File Not found {file_name}"
    return data


def configure_logging(log_file_path):
    default_value = 'ERROR'
    LOG_LEVEL = os.environ.get("LOG_LEVEL", default_value)
    if LOG_LEVEL == "DEBUG":
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
            ]
        )
    else:
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
            ]
        )


# Configuration for log file path
BASE_DIR = getattr(settings, 'BASE_DIR', None)
LOG_FILE_PATH = os.path.join(BASE_DIR, 'debug.log')
configure_logging(LOG_FILE_PATH)

INTERFACE_CONFIG = {}


# Loading Interface messages to get message directions
def load_interface_config(interfaces):
    global INTERFACE_CONFIG
    for interface in interfaces:
        direction = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'intfconfig', f'{interface}_proc.json'))
        INTERFACE_CONFIG[interface] = open_file(direction)


load_interface_config(['f1ap', 'e1ap', 'ngap', 'xnap', 's1ap', 'lte', 'x2ap'])


# Loading Cause Codes for all interfaces
def load_cause_config(interface):
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'intfconfig', f'{interface}_cause.json'))
    with open(file_path, 'r') as file:
        cause_json = json.load(file)

    cause_df = pd.DataFrame(cause_json)
    return cause_df


INTERFACE_CONFIG_PD = pd.DataFrame(columns=['interface', '_ws.col.info', 'srcNode', 'dstNode'])


# Loading Interface messages to get message directions
def load_interface_config_pd(interfaces):
    global INTERFACE_CONFIG_PD
    for interface in interfaces:
        direction_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'intfconfig', f'{interface}_proc.json'))
        interface_data = open_file(direction_file)

        temp_data = []
        for message, directions in interface_data.get(interface, {}).get('_ws.col.info', {}).items():
            temp_data.append({
                'interface': interface,
                '_ws.col.info': message,
                'srcNode': directions.get('srcNode'),
                'dstNode': directions.get('dstNode')
            })
        INTERFACE_CONFIG_PD = pd.concat([INTERFACE_CONFIG_PD, pd.DataFrame(temp_data)], ignore_index=True)
        logging.error(f"No of messages in config:{interface} - {INTERFACE_CONFIG_PD.shape}")


# Load interface configuration into DataFrame
load_interface_config_pd(['f1ap', 'e1ap', 'ngap', 'xnap', 's1ap', 'lte_rrc', 'x2ap'])


def get_direction(message, interface):
    if isinstance(message, list):
        message = message[0]

    directions = INTERFACE_CONFIG.get(interface)

    if directions is None:
        logging.warning(f'INTERFACE_CONFIG not found for interface: {interface}')
        return None, None

    for key, values in directions.items():
        if key.lower() == message.lower():
            directions = values

    src_node = directions.get("srcNode")
    dst_node = directions.get("dstNode")
    if src_node is None:
        logging.error(f' message is not found in  {interface}, message {message}')

    return src_node, dst_node


def get_interface_from_protocol(protocol):
    if "f1ap" in protocol.lower():
        return "f1ap"
    elif "ngap" in protocol.lower():
        return "ngap"
    elif "e1ap" in protocol.lower():
        return "e1ap"
    elif "xnap" in protocol.lower():
        return "xnap"
    if "lte_rrc" in protocol.lower():
        return "lte"
    elif "s1ap" in protocol.lower():
        return "s1ap"
    elif "x2ap" in protocol.lower():
        return "x2ap"
    else:
        return "unknown"
