
import time
import os
import json
import base64
import re
import socket
import array
import struct
import fcntl 
from apminsight import constants
from apminsight.logger import agentlogger

try:
    from collections.abc import Callable  # noqa
except ImportError:
    from collections import Callable  # noqa

def current_milli_time():
    return int(round(time.time() * 1000))

def is_non_empty_string(string):
    if not isinstance(string, str) or string == '':
        return False
    return True

def is_empty_string(string):
    if not isinstance(string, str) or string == '':
        return True

    return False

def is_digit(char):
    if char >= '0' and char <= '9':
        return True

    return False

def is_callable(fn):
    return isinstance(fn, Callable)

def is_ext_comp(component_name):
    return component_name in constants.ext_components

def check_and_create_base_dir():
    try:
        base_path = os.path.join(os.getcwd(), constants.base_dir)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
    except Exception:
        print('Error while creating agent base dir in '+ os.getcwd())
    
    return base_path

def get_masked_query(sql):
    if is_empty_string(sql):
        return ''
    masked_string_arguments = re.sub(r'[\'"](.*?)[\'"]', '?', sql)
    final_masked_query = re.sub(r'\d+\.\d+|\d+', '?', masked_string_arguments)
    return final_masked_query

def convert_tobase64(string):
    try:
        base64_bytes = string.encode('ascii')
        base64_value = base64.b64encode(base64_bytes)
        return base64_value.decode('ascii')
    except:
        agentlogger.exception('while base64 encoding the data')
    return ''
    
def read_config_file():
    config = {}
    try:
        current_directory = os.getcwd()
        apminsight_info_file_path = os.path.join(current_directory, constants.AGENT_CONFIG_INFO_FILE_NAME)
        if os.path.exists(apminsight_info_file_path):
            with open(apminsight_info_file_path,'r') as fh:
                config=json.load(fh)
        config = {config_key.lower(): config_value for config_key,config_value in config.items()}
    except:
        agentlogger.exception('while reading config file')
    return config

def remove_null_keys(dict):
    keys = [key for key, value in dict.items() if value is None]
    for key in keys:
        del dict[key]
        
def get_local_interfaces():
    """ Returns a dictionary of name:ip key value pairs. """
    MAX_BYTES = 4096 # Max bytes defined for interface
    FILL_CHAR = b'\0' # Empty byte character
    SIOCGIFCONF = 0x8912 # Socket configuration control 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Datagram socket is defined 
    names = array.array('B', MAX_BYTES * FILL_CHAR) # Empty byte array is defined with max bytes size of interface
    names_address, _ = names.buffer_info() # provides the address and size of bytes array created
    mutable_byte_buffer = struct.pack('iL', MAX_BYTES, names_address)
    mutated_byte_buffer = fcntl.ioctl(sock.fileno(), SIOCGIFCONF, mutable_byte_buffer)
    max_bytes_out, _ = struct.unpack('iL', mutated_byte_buffer)
    namestr = names.tobytes()
    ip_dict = {}
    for i in range(0, max_bytes_out, 40):
        name = namestr[ i: i + 16 ].split(FILL_CHAR, 1)[0]
        name = name.decode('utf-8')
        ip_bytes = namestr[i + 20:i + 24]
        full_addr = []
        for netaddr in ip_bytes:
            if isinstance(netaddr, int):
                full_addr.append(str(netaddr))
            elif isinstance(netaddr, str):
                full_addr.append(str(ord(netaddr)))
        ip_dict[name] = '.'.join(full_addr)

    return ip_dict

def get_current_stacktrace():
    stacktrace = []
    import traceback
    tracelist = traceback.extract_stack()
    for trace in tracelist:
        if not 'apminsight' in trace.filename:
            stacktrace.append(['', trace.filename, trace.name, trace.lineno])
    return stacktrace[-25:]