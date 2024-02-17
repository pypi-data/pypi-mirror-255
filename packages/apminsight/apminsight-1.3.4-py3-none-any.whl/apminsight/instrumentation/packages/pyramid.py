
from apminsight import constants
from apminsight.context import get_cur_txn, is_no_active_txn
from apminsight.logger import agentlogger
from apminsight.instrumentation.wrapper import wsgi_wrapper

def get_status_code(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)
    
        cur_txn = get_cur_txn()
        try:
            from pyramid.httpexceptions import HTTPException
            if isinstance(args[0], HTTPException):
                cur_txn.set_status_code(int(args[0]))
        except:
            agentlogger.exception('Exception occured while getting Status Code')
        return original(*args, **kwargs)
    return wrapper

def wrap_invoke_request(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn() or not get_cur_txn().get_dt_response_headers():
            return original(*args, **kwargs)
        try:
            res = original(*args, **kwargs)
        except Exception as exc:
            raise exc
        try:
            cur_txn = get_cur_txn()
            res._headers[constants.DTDATA] = cur_txn.get_dt_response_headers()
        except:
            agentlogger.exception('while adding header response for ditributed trace')
        return res
    return wrapper

module_info = {
    'pyramid.router' : [
        {
            constants.class_str : 'Router',
            constants.method_str : '__call__',
            constants.wrapper_str : wsgi_wrapper,
            constants.DT_LK_KEY : constants.LICENSE_KEY_FOR_DT_REQUEST_HTTP,
            constants.component_str : constants.pyramid_comp
        },
        {
            constants.class_str : 'Router',
            constants.method_str : 'invoke_request',
            constants.wrapper_str : wrap_invoke_request,
            constants.component_str : constants.pyramid_comp
        },
    ],
    'pyramid.config.views': [
        {
            constants.class_str : 'ViewsConfiguratorMixin',
            constants.method_str : '_derive_view',
            constants.component_str : constants.pyramid_comp,
            constants.wrap_args_str : 1
        }
    ],
    'pyramid.renderers' : [
        {
            constants.class_str : 'RendererHelper',
            constants.method_str : 'render',
            constants.component_str : constants.template,
        }
    ],
    'pyramid.httpexceptions' : [
        {
            constants.class_str : 'HTTPException',
            constants.method_str : '__call__',
            constants.wrapper_str : get_status_code,
            constants.component_str : constants.pyramid_comp,
        }
    ]
}