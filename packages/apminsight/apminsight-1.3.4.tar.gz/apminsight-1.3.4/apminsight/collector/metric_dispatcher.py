import json
import socket
import threading
from queue import Queue
from apminsight import get_agent
from apminsight.logger import agentlogger
from apminsight.util import current_milli_time, is_non_empty_string, convert_tobase64


class MetricDispatcher():
    def __init__(self, config):   
        self.__dispatcher_queue = Queue()
        self.__started = False
        self.__agent_last_communicated = None
        self.__event = threading.Event()
        
    def __push_to_dispatcher_queue(self, txn):
        self.__dispatcher_queue.put(txn)
        agentlogger.info("Successfully pushed data to Dispatcher queue")
    
    def has_started(self):
        return self.__started
    
    def __set_event(self):
        self.__event.set()
        
    def clear_event(self):
        self.__event.clear()
        
    def get_agent_last_communicated(self):
        return self.__agent_last_communicated
    
    def start_dispatching(self):
        try:
            if self.__started is True:
                return
            metric_dispatcher_thread = threading.Thread(target=self.__background_task, args=(60,), kwargs={}, daemon=True)
            metric_dispatcher_thread.start()
            self.__started = True
        except Exception :
            agentlogger.exception('Error while starting background task')

    def __background_task(self, timeout):
        while True:
            try:   
                if not self.__dispatcher_queue.empty():
                    txn_payload = self.__dispatcher_queue.get(block = False)
                    self.__send_metric_data(txn_payload)
                else:
                    event_set = self.__event.wait(timeout)
                    if event_set:
                        continue
                    else:
                        pass
                        #get_agent().update_threshold_config()
            except:
                agentlogger.exception('in background task')
        
    def __send_metric_data(self, metric_payload):
        if metric_payload:
            config = get_agent().get_config()
            try:
                HOST = config.get_exporter_host()  # The server's hostname or IP address
                PORT = int(config.get_exporter_data_port())  # The port used by the server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(bytes(metric_payload, encoding="utf-8"))
                    s.close()
                    self.__agent_last_communicated = current_milli_time()
                    self.__event.clear()
                    agentlogger.info("Successfully pushed payload to DataExporter")
            except ConnectionRefusedError:
                agentlogger.info('Error while sending data to DataExporter, please check if the exporter is running')
            except:
                agentlogger.exception('while sending metric data')

    def send_connect_data(self, payload):
        try:
            config = get_agent().get_config()
            HOST = config.get_exporter_host()  # The server's hostname or IP address
            PORT = int(config.get_exporter_status_port())  # The port used by the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(bytes(payload, encoding="utf-8"))
                data = s.recv(1024)
                s.close()
                self.__agent_last_communicated = current_milli_time()
            return data
        except ConnectionRefusedError:
            agentlogger.info('Error while Connecting to DataExporter, please check if the exporter is running')
        except:
            agentlogger.exception('while getting transaction data')
    
    async def construct_payload(self, metric_constructor, external=None):
        try:
            payload = self.__create_json_to_send(metric_constructor())
            if external:
                agentlogger.info('Successfully constructed payload recieved from S247'+ external+ 'agent')
            else:
                agentlogger.info('Successfully constructed tansaction payload')
            self.__push_to_dispatcher_queue(payload)
            self.__set_event()
        except:
            agentlogger.exception('while constructing data payload to exporter')
    
    def __create_json_to_send(self, payload):
        json_to_exporter = convert_tobase64(json.dumps(payload))
        if is_non_empty_string(json_to_exporter):
            json_to_exporter+="\n"
        return json_to_exporter
    
