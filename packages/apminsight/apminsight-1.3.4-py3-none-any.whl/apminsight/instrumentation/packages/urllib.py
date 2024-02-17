import urllib
from http.client import HTTPResponse
from urllib.error import HTTPError
from urllib.request import Request

from apminsight import constants
from apminsight.logger import agentlogger

def get_request_status(return_value, error):
    if isinstance(return_value, HTTPResponse):
        return str(return_value.status)
    elif isinstance(error, HTTPError):
        return str(error.code)
        
    return None

def get_request_url_method(fullurl):
    if isinstance(fullurl,Request):
        return  fullurl.get_full_url(), fullurl.get_method()
    elif isinstance(fullurl,str):
        return fullurl,'GET'
    
    return None, None

def extract_urllib_request(tracker, args=(), kwargs={}, return_value=None, error=None):
    try:
        if args:
            method = ''
            url = ''
            status = ''
            url, method = get_request_url_method(args[1])
            
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.hostname
            port = parsed_url.port
            scheme = parsed_url.scheme
            if port is None:
                port = 443 if scheme=='https' else 80
            
            status = get_request_status(return_value,error)
            if status:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + status + ' - ' + url)
            else:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + url)
            tracker.set_info({constants.HTTP_METHOD: method, constants.HOST: host, constants.PORT: port, "url": url, constants.STATUS: status})

    except Exception as exc:
        agentlogger.exception("while Extracting URLLIB request")

module_info = {
    
    'urllib.request' : [
        {   constants.class_str : 'OpenerDirector',
            constants.method_str : 'open',
            constants.component_str : constants.http_comp,
            constants.extract_info_str : extract_urllib_request
        }
    ]
}

