
from apminsight import constants
from apminsight.logger import agentlogger
from apminsight.context import is_no_active_txn, get_cur_txn
from apminsight.agentfactory import get_agent
from apminsight.instrumentation.wrapper import default_wrapper

def wrap_urlopen(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)
        if not kwargs or not isinstance(kwargs, dict) or not kwargs.get('headers'):
            return default_wrapper(original, module, method_info)(*args, **kwargs)
        try:
            license_key_for_dt = get_agent().get_config().get_license_key_for_dt()
            kwargs.get('headers').update({constants.LICENSE_KEY_FOR_DT_REQUEST : license_key_for_dt})
            get_cur_txn().dt_req_headers_injected(True)
        except:
            agentlogger.exception('while adding request headers for distributed trace')
        return default_wrapper(original, module, method_info)(*args, **kwargs)
    return wrapper

def get_request_url(conn,args, kwargs):
    from urllib3.connectionpool import HTTPSConnection
    if isinstance(conn, HTTPSConnection):
        return 'https://' + conn.host + kwargs.get(constants.URL)
    else:
        return 'http://' + conn.host + kwargs.get(constants.URL)


def get_conn_object(args):
    if len(args) :
        return args[0]
    return None

def get_conn_host_port( conn):
    if conn:
        return conn.host, conn.port
    return None, None
    
def extract_urllib3_request(tracker, args=(), kwargs={}, return_value=None, error=None):
    try:
        conn = get_conn_object(args)
        host, port = get_conn_host_port(conn) 
        method = ""
        url = ""
        
        if conn and len(args)==1:
            method = 'REQUESTS' + ' - ' + kwargs.get('method')
            url  = get_request_url(conn, args, kwargs)   
        elif len(args)==3:
            method = args[1]
            url = kwargs.get(constants.REQUEST_URL)

        if conn:
            status = str(return_value.status) if return_value is not None else None
            if status:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + status + ' - ' + url)
                tracker.set_as_http_err() if int(status) >= 400 else 0
            else:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + url)
            tracker.set_info({constants.HTTP_METHOD: method, constants.HOST: host, constants.PORT: port, constants.URL: url, constants.STATUS: status})

    except:
        agentlogger.exception("while extracting URLLIB3 request")

module_info = {

    'urllib3.connectionpool' : [
        {   constants.class_str : 'HTTPConnectionPool',
            constants.method_str : 'urlopen',
            constants.component_str : constants.http_comp,
            constants.wrapper_str : wrap_urlopen,
            constants.extract_info_str : extract_urllib3_request
        }
    ],
}
