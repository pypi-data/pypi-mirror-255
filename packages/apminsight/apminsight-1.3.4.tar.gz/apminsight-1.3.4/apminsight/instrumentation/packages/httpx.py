from apminsight import constants
from apminsight.agentfactory import get_agent
from apminsight.context import get_cur_tracker, is_no_active_txn, set_cur_tracker
from apminsight.instrumentation.util import create_tracker_info
from apminsight.instrumentation.wrapper import handle_tracker_end
from apminsight.logger import agentlogger
from apminsight.instrumentation.http_util import handle_dt_response_headers

def wrap_send(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)

        if len(args)>1:
            try:
                request = args[1]
                license_key_for_dt = get_agent().get_config().get_license_key_for_dt()
                request.headers.update({constants.LICENSE_KEY_FOR_DT_REQUEST : license_key_for_dt})
            except:
                agentlogger.exception('while adding request headers for distributed trace')
        res = None 
        err = None
        agent = get_agent()
        parent_tracker = get_cur_tracker()
        tracker_info = create_tracker_info(module, method_info, parent_tracker)
        cur_tracker = agent.check_and_create_tracker(tracker_info)
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
            
def extract_req(tracker, args=(), kwargs={}, return_value=None, error=None):
    try:
        if args:
            request = args[1]
            method = request.method
            url = request.url
            url_str = str(url)
            host = url.host
            port = url.port
            status = str(return_value.status_code) if return_value else None
            handle_dt_response_headers(return_value)
            if status:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + status + ' - ' + url_str)
                tracker.set_as_http_err() if int(status) >= 400 else 0
            else:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + url_str)
            info = {constants.HTTP_METHOD: method, constants.HTTP: host, constants.PORT: port, constants.URL: url_str, constants.STATUS: status}
            tracker.set_info(info)
    except Exception as exc:
        agentlogger.exception("while extracting HTTPX request")

module_info = {
    'httpx._client' : [
        {   constants.class_str : 'Client',
            constants.method_str : 'send',
            constants.component_str : constants.http_comp,
            constants.wrapper_str : wrap_send,
            constants.extract_info_str : extract_req,
        },
    ],
}
