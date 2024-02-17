
import os
import apminsight
import platform
import json
import apminsight.constants as constants
from apminsight.logger import agentlogger
from .config_util import ConfigReader
from apminsight.util import is_empty_string, is_non_empty_string, get_local_interfaces

class Configuration:
    __license_key = None
    __app_name = None
    __app_port =  None
    __app_port_set = None
    __collector_host = None
    __collector_host = None
    __proxy_server_host = None
    __proxy_server_port = None
    __proxy_username = None
    __proxy_password = None
    __agent_version = None
    __installed_path = None
    __cloud_instance_id = None
    __is_cloud_instance = None
    __cloud_type = None
    __exporter = None
    __exporter_status_port = None
    __exporter_data_port = None
    __exporter_host = None
    __host_type = None
    __is_docker = None
    __host_name = None
    __fqdn = None
    __conn_payload=None
    __ipv4 = []
    __process_cpu_threshold = None

    def __init__(self, info):
        self.__license_key = None#get_license_key(info)   Not reading from user config
        self.__app_name = ConfigReader.get_app_name(info)
        self.__app_port = None
        self.__app_port_set = False
        self.__collector_host = ConfigReader.get_collector_host(self.__license_key, info)
        self.__collector_port = ConfigReader.get_collector_port(info)
        self.__proxy_server_host = ConfigReader.get_proxy_server_host(info)
        self.__proxy_server_port = ConfigReader.get_proxy_server_port(info)
        self.__proxy_username = ConfigReader.get_proxy_auth_username(info)
        self.__proxy_password = ConfigReader.get_proxy_auth_password(info)
        self.__agent_version = apminsight.version
        payload_config = os.getenv(constants.apm_print_payload, '')
        self.print_payload = False if is_empty_string(payload_config) else True
        self.__installed_path = apminsight.installed_path
        self.__is_cloud_instance, self.__cloud_type, self.__cloud_instance_id = ConfigReader.get_cloud_details() if not ConfigReader.using_exporter(info) else (None, None, None)
        self.__exporter = ConfigReader.using_exporter(info)
        self.__exporter_status_port = ConfigReader.get_exporter_status_port(info)
        self.__exporter_data_port = ConfigReader.get_exporter_data_port(info)
        self.__exporter_host = ConfigReader.get_exporter_host(info)
        self.__is_docker, self.__host_type, self.__host_name = ConfigReader.get_docker_env_details()
        self.__fqdn = ConfigReader.get_fqdn()
        self.__ipv4 = get_ipv4_address()
        self.__conn_payload = self.create_connection_payload()
        self.__process_cpu_threshold = ConfigReader.get_process_cpu_threshold()
        
    def is_configured_properly(self):
        if is_empty_string(self.__license_key):
            return False
       
        return True

    def update_collector_info(self, collector_info):
        if collector_info is None:
            return

        try:
            self.__collector_host = collector_info.get(constants.host_str, self.__collector_host)
            self.__collector_port = collector_info.get(constants.port_str, self.__collector_port)
        except Exception:
            agentlogger.exception('while updating collector info')
            
    def get_license_key(self):
        return self.__license_key

    def get_app_name(self):
        return self.__app_name

    def set_app_name(self, appname):
        self.__app_name = appname
        
    def get_app_port(self, for_exporter=True):
        if self.__app_port is not None:
            if not for_exporter or not self.__exporter:
                return self.__app_port
            return int(self.__app_port)
        
    def set_app_port(self, app_port):
        self.__app_port = app_port
        self.__conn_payload['connect_info']['agent_info']['port'] = int(app_port)
        self.__app_port_set = True
        
    def app_port_set(self):
        return self.__app_port_set
    
    def get_collector_host(self):
        return self.__collector_host

    def get_collector_port(self):
        return self.__collector_port

    def get_agent_version(self):
        return self.__agent_version

    def get_installed_dir(self):
        return self.__installed_path

    def is_payload_print_enabled(self):
        return self.print_payload
    
    def get_is_cloud_instance(self):
        return self.__is_cloud_instance

    def get_cloud_instance_id(self):
        return self.__cloud_instance_id

    def get_cloud_type(self):
        return self.__cloud_type

    def get_fqdn(self):
        return self.__fqdn
        
    def get_host_name(self, for_exporter=True):
        if self.__is_docker:
            return self.__host_name
        if not for_exporter or not self.__exporter and self.__cloud_instance_id:
            return self.__cloud_instance_id
        return platform.node()
        
    def get_host_type(self, for_exporter=True):
        if self.__is_docker:
            return self.__host_type
        if not for_exporter or not self.__exporter and self.__cloud_type:
            return self.__cloud_type
        return platform.system()

    def get_proxy_details(self):
        if not self.__proxy_server_host or not self.__proxy_server_port:
            return False
        if self.__proxy_username and self.__proxy_password :
            proxy_details = { 'http': 'http://' + self.__proxy_username + ':' + self.__proxy_password + '@' + self.__proxy_server_host + ':' + self.__proxy_server_port,
                    'https': 'http://' + self.__proxy_username + ':' + self.__proxy_password + '@' + self.__proxy_server_host + ':' + self.__proxy_server_port
                    }
        else:
            proxy_details = { 'http': 'http://' + self.__proxy_server_host + ':' + self.__proxy_server_port,
                    'https': 'http://' + self.__proxy_server_host + ':' + self.__proxy_server_port
                    }
        return proxy_details

    def is_using_exporter(self):
        return self.__exporter

    def get_exporter_status_port(self):
        return self.__exporter_status_port 
        
    def get_exporter_data_port(self):
        return self.__exporter_data_port

    def get_exporter_host(self):
        return self.__exporter_host

    def set_license_key(self, license_str):
        if is_non_empty_string(license_str):
            self.__license_key = license_str
    
    def get_ipv4(self):
        return self.__ipv4
    
    def get_process_cpu_threshold(self):
        return self.__process_cpu_threshold
    
    def get_user_setup_config(self):
        return {
                        constants.APP_NAME : self.get_app_name(),
                        constants.HOST_NAME : self.get_host_name(),
                        constants.APP_PORT : self.get_app_port(),
                        constants.EXP_HOST : self.get_exporter_host(),
                        constants.EXP_STATUS_PORT : self.get_exporter_status_port(),
                        constants.EXP_DATA_PORT : self.get_exporter_data_port(),
                        constants.PROXY_DETAILS : self.get_proxy_details(),
                        constants.AGENT_VERSION : self.get_agent_version()
            },
        
    def get_license_key_for_dt(self):
        if self.is_configured_properly():
            license_key = self.__license_key
            license_key_for_dt = license_key[-12:]
            return license_key_for_dt
        return None
    def create_connection_payload(self):
        conn_payload = {
                "agent_info" : { 
                "application.type": constants.python_str, 
                "agent.version": self.get_agent_version()[: self.get_agent_version().index(".",self.get_agent_version().index(".")+1)], 
                "agent.version.info": self.get_agent_version(),
                "application.name": self.get_app_name(), 
                "port": self.get_app_port() or 8080, 
                "host.type": self.get_host_type(),
                "hostname": self.get_host_name(),
                "fqdn" : self.get_fqdn()
            }, "environment" : { 
                "IP" : self.get_ipv4(),
                #"UserName": process.env.USER, 
                "OSVersion": platform.release(), 
                "MachineName": platform.node(), 
                'AgentInstallPath': self.get_installed_dir(), 
                "Python version": platform.python_version(), 
                "OSArch": platform.machine(), 
                "OS": platform.system(),
                "Python implementation" : platform.python_implementation()
            }
        }
        if self.is_using_exporter():
            conn_payload = { 
            "connect_info" : conn_payload,
            "misc_info" : {}
        }
        
        return conn_payload

    def get_conn_payload(self, txn_name='Anonymous'):
        conn_payload = self.__conn_payload
        conn_payload["misc_info"]["txn.name"] = txn_name
        if self.is_using_exporter():
            conn_payload = json.dumps(conn_payload)
            conn_payload+="\n"
        return conn_payload

def get_ipv4_address():
    ip_dict = get_local_interfaces()
    if len(ip_dict):
        return list(ip_dict.values())
    return []
