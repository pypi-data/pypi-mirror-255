
import functools
from apminsight.context import get_cur_txn, clear_cur_context
from apminsight.agentfactory import get_agent
from apminsight.constants import method_str, TRACKER_NAME

class CustomApiProvider:

    @staticmethod
    def background_transaction(bgtxn_name="AnonymousBgTxn"):
        def background_wrapper(original):
            @functools.wraps(original)
            def wrapper(*args, **kwargs):
                from apminsight.instrumentation.util import create_tracker_info
                from apminsight.logger import agentlogger
                if get_cur_txn():
                    agentlogger.info('Cannot create a BackGround Transaction object while there is an active WebTxn')
                    return original(*args, **kwargs)
                cur_txn = None
                res = None 
                agent = get_agent()
                try:
                    txn_name = bgtxn_name if bgtxn_name != "" else original.__name__
                    method_info = {method_str:original.__name__}
                    tracker_info = create_tracker_info(original.__module__, method_info)
                    cur_txn = agent.check_and_create_bgtxn(txn_name, tracker_info)
                    res = original(*args, **kwargs)
                    agent.end_txn(cur_txn, res)
                except Exception as exc:
                    agent.end_txn(cur_txn,err=exc)
                    raise exc
                finally:
                    clear_cur_context()
                return res
            return wrapper
        return background_wrapper
    
background_transaction = CustomApiProvider.background_transaction