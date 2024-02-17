from apminsight import constants
from apminsight.agentfactory import get_agent
from apminsight.context import get_cur_tracker, is_no_active_txn, get_cur_txn, set_cur_tracker
from apminsight.constants import extract_info_str
from apminsight.instrumentation.util import create_tracker_info
from apminsight.logger import agentlogger
from apminsight.instrumentation.wrapper import handle_tracker_end
from apminsight.util import current_milli_time
from apminsight.metric.tracker import Tracker
from http.client import HTTPConnection
from apminsight.instrumentation.http_util import handle_dt_response_headers

def wrap_request(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)
        res = None 
        err = None
        cur_tracker = None
        agent = get_agent()
        if len(args)>4 and not get_cur_txn().dt_req_headers_injected():
            try:
                license_key_for_dt = get_agent().get_config().get_license_key_for_dt()
                args[4].update({constants.LICENSE_KEY_FOR_DT_REQUEST : license_key_for_dt})
                get_cur_txn().dt_req_headers_injected(True)
            except:
                agentlogger.exception('while adding request headers for distributed trace')
                
        parent_tracker = get_cur_tracker()
        if isinstance(parent_tracker, Tracker) and parent_tracker.get_component()==constants.http_comp:
            return original(*args, **kwargs)
        try:
            agent = get_agent()
            tracker_info = create_tracker_info(module, method_info, parent_tracker)
            cur_tracker = agent.check_and_create_tracker(tracker_info)
        except:
            agentlogger.exception("in wrap_request function")
        try:
            res = original(*args, **kwargs)
        except Exception as exc:
            err = exc
            raise exc
        finally:
            handle_tracker_end(cur_tracker, method_info, args, kwargs, res, err)
            set_cur_tracker(parent_tracker)
        return res

    # special handling for flask route decorator
    wrapper.__name__ = original.__name__
    return wrapper

def extract_request(tracker, args=(), kwargs={}, return_value=None, error = None):
    try:
        if len(args)>0 :
            conn = args[0]
            method = str(args[1])
            path = str(args[2])
            host = str(conn.host)
            port = int(conn.port)
            
            def construct_url(conn, host, path):
                http_protocol = 'http' if isinstance(conn,HTTPConnection) else 'https'
                return http_protocol + '://' + host + path
            
            url = construct_url(conn, host, path)
            tracker_name = tracker.get_tracker_name() + " : "+ method + " - " + url
            tracker.set_tracker_name(tracker_name)
            tracker.set_info({constants.HTTP_METHOD : method, constants.URL : url, constants.HOST : host, constants.PORT : port,  constants.METHOD:"request", constants.CLASS:"HTTPConnection"})

    except:
        agentlogger.exception("Error while extracting HTTP/HTTPS call info")

def end_tracker(tracker, err):
    # consider child overhead time
    if err is not None:
        tracker.mark_error(err)
    previous_end_time = tracker.get_end_time()
    tracker.set_end_time(current_milli_time())
    total_time = tracker.get_end_time() - previous_end_time
    tracker.set_rt(total_time - tracker.get_child_overhead())
    if tracker.get_parent() is not None:
        tracker.get_parent().update_child_overhead(total_time)
    if tracker.is_distributed_trace():
            get_cur_txn().increment_dt_count()

    tracker.complete()

def wrap_and_remove_child_tracker(original, module, method_info, args,kwargs):
    try:
        res = None
        err = None
        res = original(*args, **kwargs)
    except Exception as exc:
        err = exc
        raise err
    finally:
        try:
            cur_tracker = get_cur_tracker()
            main_tracker = cur_tracker.get_child_trackers()[-1]
            if isinstance(main_tracker, Tracker) is not True:
                return
                
            handle_dt_response_headers(res)

            if type(method_info) is dict and extract_info_str in method_info:
                extractor = method_info[extract_info_str]
                extractor(main_tracker, args=args, kwargs=kwargs, return_value=res, error = err)

            end_tracker(main_tracker,err= err)
        except Exception:
            agentlogger.exception("While handling tracker end")
    return res
        
def new_response_tracker(original, module, method_info, *args, **kwargs):
    agent = get_agent()
    res = None
    err = None
    cur_tracker = None
    parent_tracker = get_cur_tracker()
    tracker_info = create_tracker_info(module, method_info, parent_tracker)
    try:
        cur_tracker = agent.check_and_create_tracker(tracker_info)
    except:
        agentlogger.exception('while creating http tracker')
    try:
        res = original(*args, **kwargs)
    except Exception as exc:
        err = exc
        raise err
    finally:
        handle_dt_response_headers(res)
        cur_tracker.end_tracker(err)
        set_cur_tracker(parent_tracker)

    return res

def wrap_getresponse(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)
        cur_tracker = get_cur_tracker()
        if cur_tracker.get_component()==constants.http_comp:
            res = None
            try:
                res = original(*args, **kwargs)
            except Exception as exc:
                raise exc
            handle_dt_response_headers(res)
            return res
        
        if cur_tracker is not None and cur_tracker.get_child_trackers() != [] and cur_tracker.get_child_trackers()[-1].get_info("method") == "request" and cur_tracker.get_child_trackers()[-1].get_info("class") == "HTTPConnection":
            #Remove request child tracker and assign http call to current tracker for http modules
            res = wrap_and_remove_child_tracker(original,module, method_info,args, kwargs)
        else:
            res = new_response_tracker(original, module, method_info, *args, **kwargs)
        return res

    # special handling for flask route decorator
    wrapper.__name__ = original.__name__
    return wrapper

def extract_getresponse(tracker, args=(), kwargs={}, return_value=None, error = None):
    if hasattr(return_value, constants.STATUS):
        status = return_value.status
        if status:
            tracker.set_tracker_name(tracker.get_actual_method() + " : "+ tracker.get_info(constants.HTTP_METHOD) + ' - ' + str(status) + ' - ' + tracker.get_info(constants.URL))
            tracker.set_as_http_err() if int(status) >= 400 else 0
            info = {constants.STATUS: status}
            tracker.set_info(info)

module_info = {
    'http.client' : [
        {   constants.class_str : 'HTTPConnection',
            constants.method_str : '_send_request',
            constants.component_str : constants.http_comp,
            constants.wrapper_str : wrap_request,
            constants.extract_info_str : extract_request,
        },
        {   constants.class_str : 'HTTPConnection',
            constants.method_str : 'getresponse',
            constants.component_str : constants.http_comp,
            constants.wrapper_str : wrap_getresponse,
            constants.extract_info_str : extract_getresponse,
        },
    ],
}
