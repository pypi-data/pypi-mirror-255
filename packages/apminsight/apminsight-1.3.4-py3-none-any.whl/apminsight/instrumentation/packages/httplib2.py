from apminsight import constants
from apminsight.logger import agentlogger

def extract_req(tracker, args=(), kwargs={}, return_value=None, error=None):
    try:
        if args:
            conn = args[1]
            host = conn.host
            port = conn.port
            method = args[5]
            url = args[3]
            status = ''
            if return_value:
                status = str(return_value[0].status)
            if status:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + status + ' - ' + url)
                tracker.set_as_http_err() if int(status) >= 400 else 0
            else:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + url)
            info = {constants.HTTP_METHOD: method, constants.HOST: host, constants.PORT: port, constants.URL: url, constants.STATUS: status}
            tracker.set_info(info)

    except:
        agentlogger.exception("while extracting HTTPX request")

module_info = {
    'httplib2' : [
        {   constants.class_str : 'Http',
            constants.method_str : '_request',
            constants.component_str : constants.http_comp,
            constants.extract_info_str : extract_req,
        },
    ],
}
