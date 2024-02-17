import os
import threading
import time
import psutil
from apminsight.constants import PROCESS_CPU_THRESHOLD_VAL
from apminsight.logger import agentlogger

class CPUUtilization():

    def __init__(self, cpu_threshold=PROCESS_CPU_THRESHOLD_VAL):
        self._cpu_percent = 0.0
        self._thread_status = False
        self.cpu_threshold_status = False
        self.cpu_threshold_val = cpu_threshold
        self._lock = threading.Lock()
        self.pid = os.getpid()
        self._num_cores = psutil.cpu_count()
        self.process = psutil.Process(self.pid)
        self._proc_cpu_percent = self.process.cpu_percent(interval=0)/self._num_cores
        self.start_cpu_stats_thread()

    def start_cpu_stats_thread(self):
        if not self._thread_status:
            self.thread = threading.Thread(target= self.cpu_utilization, daemon=True)
            self.thread.start()
            self._thread_status = True
    
    def get_cpu_threshold_status(self):
        return self.cpu_threshold_status
    
    def update_cpu_threshold_status(self, process_cpu_val):
        self.cpu_threshold_status = True if process_cpu_val > self.cpu_threshold_val else False

    def get_process(self):
        if os.getpid() != self.pid:
            self.pid = os.getpid()
            self.process = psutil.Process(self.pid)
        return self.process
    
    def cpu_utilization(self):
        agentlogger.info("CPU utilization stats thread started")
        while True:
            try:
                with self._lock:
                    self._cpu_percent = psutil.cpu_percent()
                    self._proc_cpu_percent = self.get_process().cpu_percent(interval=0)/self._num_cores
                    self.update_cpu_threshold_status(self._proc_cpu_percent)
                    agentlogger.info(f"CPU Utilization for process with PID {self.pid}: {self._proc_cpu_percent}%")
            except Exception as exc:
                agentlogger.info(f"Exception in CPU utilization thread {exc}%")
            finally:
                time.sleep(60)

    def get_cpu_utilization(self):
        with self._lock:
            return self._proc_cpu_percent

