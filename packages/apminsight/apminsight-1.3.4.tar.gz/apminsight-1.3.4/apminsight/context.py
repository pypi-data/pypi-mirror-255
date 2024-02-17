
import threading
from apminsight import constants
from apminsight.agentfactory import get_agent

thread_local = threading.local()

def set_async_txn_trace_id(trace_id):
    setattr(thread_local, 'apm_async_txn_trace_id', trace_id)

def set_async_tracker_span_id(span_id):
    setattr(thread_local, 'apm_async_tracker_span_id', span_id)

def set_async_context(context):
    set_async_txn_trace_id(context.get(constants.TRACE_ID_STR))
    set_async_tracker_span_id(context.get(constants.SPAN_ID_STR))

def get_cur_async_context():
    return {
      constants.SPAN_ID_STR  : get_async_tracker_span_id(),
      constants.TRACE_ID_STR : get_async_txn_trace_id()
    }
    
def get_async_txn_trace_id():
    return getattr(thread_local, 'apm_async_txn_trace_id', '')

def get_async_tracker_span_id():
    return getattr(thread_local, 'apm_async_tracker_span_id', '')

def has_no_async_context():
    return not bool(get_async_txn_trace_id())

def clear_cur_async_context():
    set_cur_context(None, None)

def set_cur_txn_trace_id(trace_id):
    setattr(thread_local, 'apm_cur_txn_trace_id', trace_id)
    
def set_cur_txn(txn):
    if txn is None:
        set_cur_txn_trace_id(None)
    else:
        set_cur_txn_trace_id(txn.get_trace_id())

def set_cur_tracker(tracker):
    if tracker is None:
        set_cur_tracker_span_id(None)
    else:
        set_cur_tracker_span_id(tracker.get_span_id())
        
def set_cur_tracker_span_id(span_id):
    setattr(thread_local, 'apm_cur_tracker_span_id', span_id)

def set_cur_context(trace_id=None, span_id=None):
    set_cur_txn_trace_id(trace_id)
    set_cur_tracker_span_id(span_id)

def clear_cur_context():
    set_cur_context(None, None)

def get_cur_context():
    return {
      constants.SPAN_ID_STR  : get_cur_tracker_span_id(), 
      constants.TRACE_ID_STR : get_cur_txn_trace_id()
    }
    
def get_cur_txn_trace_id():
    return getattr(thread_local, 'apm_cur_txn_trace_id', '')
    
def get_cur_txn():
    return get_agent().get_txn(get_cur_txn_trace_id())

def get_cur_tracker_span_id():
    return getattr(thread_local, 'apm_cur_tracker_span_id', '')

def get_cur_tracker():
    return get_cur_txn().get_tracker(get_cur_tracker_span_id()) if get_cur_txn() else None

def is_txn_active():
    return bool(get_cur_txn_trace_id())

def is_no_active_txn():
    return not bool(get_cur_txn_trace_id())

