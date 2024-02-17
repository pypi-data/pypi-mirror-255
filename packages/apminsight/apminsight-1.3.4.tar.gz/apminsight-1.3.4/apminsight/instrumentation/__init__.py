
from importlib import import_module
from apminsight import constants
from apminsight.agentfactory import get_agent
from apminsight.logger import agentlogger
from apminsight.util import is_callable
from apminsight.constants import class_str, method_str, wrapper_str, wrap_args_str
from apminsight.instrumentation.modules import modules_info
from apminsight.instrumentation.wrapper import default_wrapper, args_wrapper

def check_and_instrument(module_name, act_module):
    if not module_name:
        return

    if hasattr(act_module, constants.APM_INSTRUMENTED):
        return 

    if module_name in modules_info.keys():
        methods_info = modules_info.get(module_name)
        for each_method_info in methods_info:
            instrument_method(module_name, act_module, each_method_info)

        setattr(act_module, constants.APM_INSTRUMENTED, True)
        agentlogger.info(module_name+' instrumented')


def instrument_method(module_name, act_module, method_info):
    parent_ref = act_module
    class_name = ''

    if type(method_info) is not dict:
        return

    if class_str in method_info:
        class_name = method_info.get(class_str)
        if hasattr(act_module, class_name):
            parent_ref = getattr(act_module, class_name)
            module_name = module_name+'.'+class_name

    instrument_methods = method_info.get(method_str, '')
    if isinstance(instrument_methods,str):
        method_list = []
        method_list.append(instrument_methods)
    else:
        method_list = instrument_methods

    for method in method_list:
        if hasattr(parent_ref, method):
            original = getattr(parent_ref, method)
            if not is_callable(original):
                return
            method_info[method_str] = method

            # use default wrapper if there is no wrapper attribute
            wrapper_factory = default_wrapper
            if wrap_args_str in method_info:
                wrapper_factory = args_wrapper
            elif wrapper_str in method_info:
                wrapper_factory = method_info.get(wrapper_str)
            
            ''' we are changing the same method info object to append method_str, 
                it will change existing method info object '''
            wrapper = wrapper_factory(original, module_name, method_info.copy())
            setattr(parent_ref,  method, wrapper)
    

def instrument_django_middlewares():
    methods = ['process_request', 'process_view', 'process_exception', 'process_template_response', 'process_response']
    try:
        from django.conf import settings
        
        wsgi_app = settings.WSGI_APPLICATION
        appname = wsgi_app.split('.')[0] if wsgi_app else None
        if appname and get_agent() and get_agent().get_config().get_app_name()== constants.DEFAULT_APM_APP_NAME:
            get_agent().get_config().set_app_name(appname)

        middleware = getattr(settings, constants.MIDDLEWARE, None) or \
            getattr(settings, constants.MIDDLEWARE_CLASSES, None)

        if middleware is None:
            return

        for each in middleware:
            module_path, class_name = each.rsplit('.', 1)
            act_module = import_module(module_path)
            for each_method in methods:
                method_info = {
                    constants.class_str : class_name,
                    constants.method_str : each_method,
                    constants.component_str : constants.middleware
                }
                instrument_method(module_path, act_module, method_info)
    except Exception as exc:
        agentlogger.exception(f"django middleware instrumentation error {exc} ")

initialized = False

def init_instrumentation():
    global initialized
    if initialized:
        return
    for each_mod in modules_info:
        try:
            act_module = import_module(each_mod)
            check_and_instrument(each_mod, act_module)
        except Exception:
            agentlogger.info(each_mod +' is not present')

    initialized = True

