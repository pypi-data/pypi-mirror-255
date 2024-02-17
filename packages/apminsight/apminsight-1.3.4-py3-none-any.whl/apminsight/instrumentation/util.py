
import random
import string
from apminsight.constants import *
from apminsight.metric.tracker import Tracker
from apminsight.logger import agentlogger
from apminsight.context import get_cur_async_context

def create_tracker_info(module, method_info, parent_tracker=None, async_root=False):
    tracker_info = None
    try:
        tracker_name = module + '.' + method_info[method_str]
        tracker_info = { 'name' : tracker_name }
        if isinstance(parent_tracker, Tracker):
            tracker_info[PARENT_TRACKER] = parent_tracker
            tracker_info[PARENT_CONTEXT] = parent_tracker.get_context()
        tracker_info[CONTEXT] = {
                                  TRACE_ID_STR:parent_tracker.get_trace_id() if parent_tracker else None,
                                  SPAN_ID_STR :''.join(random.choices(string.ascii_letters+string.digits, k=16))
                                }
        if async_root:
            tracker_info[IS_ASYNC] = True
            tracker_info[ASYNC_PARENT_CONTEXT] = get_cur_async_context()
        if component_str in method_info:
            tracker_info[component_str] = method_info[component_str]

        if is_db_tracker_str in method_info:
            tracker_info[is_db_tracker_str] = True

        
    except Exception:
        agentlogger.exception("while creating tracker info")
    finally:
        return tracker_info