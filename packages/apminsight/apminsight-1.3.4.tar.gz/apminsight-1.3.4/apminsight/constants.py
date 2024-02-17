
CLASS = class_str = 'class'
METHOD = method_str = 'method'
wrapper_str = 'wrapper'
COMPONENT = component_str = 'component'
wrap_args_str = 'wrap_args'
EXTRACT_INFO = extract_info_str = 'extract_info'
connect_details = "connect_details"
HOST = host_str = 'host'
PORT = port_str = 'port'
default_host_str = 'default_host'
default_port_str = 'default_port'
is_db_tracker_str = 'is_db_tracker'
localhost_str = 'localhost'
path_info_str = 'PATH_INFO'
query_string_str = 'QUERY_STRING'
request_method_str = 'REQUEST_METHOD'
server_port_str = 'SERVER_PORT'
transaction_info_str = 'transaction_info'
method_info_str = 'method_info'
level_str = 'level'
QUERY = query_str = 'query'
status_code_str = 'status_code'
proxy_class_str = 'proxy_class'
python_str = 'PYTHON'
data_str = 'data'
TRACE_ID_STR = 'trace_id'
SPAN_ID_STR = 'span_id'
CUSTOMPARAMS = 'CustomParams'
CONTEXT = 'context'
PARENT_CONTEXT = 'parent_context'
PARENT_TRACKER = 'parent'
ASYNC_PARENT_CONTEXT = 'async_parent_context'
IS_ASYNC = 'is_async'
LOGINFO = 'loginfo'
EXP_STACK_TRACE = 'exception_st'
OPERATION = 'opn'
OBJECT = 'obj'
DB_OPERATION = 'db_opn'
STACKTRACE = 'stacktrace'
HTTP_METHOD = 'http_method'
URL = 'url'
STATUS = 'status'
DEFAULT_APM_APP_NAME = 'Python-Application'
MIDDLEWARE = 'MIDDLEWARE'
MIDDLEWARE_CLASSES = 'MIDDLEWARE_CLASSES'
APPNAME = 'appname'
APP_PORT = 'app_port'
EXP_HOST = 'exporter_host'
EXP_STATUS_PORT = 'exporter_status_port'
EXP_DATA_PORT = 'exporter_data_port'
LOG_FILE_SIZE = 'log_file_size'
LOG_FILE_BACKUP_COUNT  = 'log_file_count'
DOCKER = 'DOCKER'

HOST_NAME = 'host_name'
APP_NAME = 'app_name'
PROXY_DETAILS = 'proxy_details'
AGENT_VERSION = 'agent_version'
SETUP_CONFIG = 'setup_config'
THRESHOLD_CONFIG = 'threshold_config'

exporter_param_key_http_host = 'http_host'
exporter_param_key_request_url = 't_name'
exporter_param_key_transaction_duration = 'r_time'
exporter_param_key_request_method = 'http_method_name'
exporter_param_key_bytes_in = 'bytes_in'
exporter_param_key_bytes_out = 'bytes_out'
exporter_param_key_transaction_type = 'transaction_type'
exporter_param_key_distributed_count = 'dt_count'
exporter_param_key_thread_id = 'thread_id'
exporter_param_key_response_code = 'httpcode'
exporter_param_key_collection_time = 's_time'
exporter_param_key_collection_end_time = 'e_time'
exporter_param_key_cpu_time = 'cputime'
exporter_param_key_memory_usage = 'memory_usage'
exporter_param_key_method_count = 'method_count'
exporter_param_key_trace_id = 'trace_id'
exporter_param_key_instance_id = 'instance_id'
exporter_param_key_request_headers = 'request_headers'
exporter_param_key_custom_params = 'custom_params'
exporter_param_key_query_string = 'http_query_str'
exporter_param_key_application_type = 'application_type'
exporter_param_key_application_name = 'application_name'
exporter_param_key_bytes_in = 'bytes_in'
exporter_param_key_bytes_out = 'bytes_out'
exporter_param_key_memory_usage = 'memalloc'
exporter_param_key_session_id = 'session_id'
exporter_param_key_rum_appkey = 'rum_appkey'
exporter_param_key_http_headers = 'http_headers'
exporter_param_key_http_input_params = 'http_input_params'
exporter_param_key_async = 'async'

SH_ASYNC_ROOT = 'ar'
SH_EXT_COMP = 'ex'
SH_IS_FAULT = 'if'
SH_IS_ERROR = 'ie'
SH_HOST_NAME = 'hn'
SH_PORT_NUMBER = 'pn'
SH_STACK_TRACE = SH_START_TIME = 'st'
SH_END_TIME = 'et'
SH_FUN_NAME = 'fn'
SH_COMP_NAME= 'cn'
SH_SPAN_ID = 'si'
SH_PAR_SPAN_ID = 'psi'
SH_QUERY_STR = 'qs'
SH_DIST_TRACE = 'dt'
SH_ERR_MSG = SH_STRING = 'str'
SH_ERR_CLS = 'err_clz'
SH_ERR_INFO = 'ei'
SH_ERR_STACK_TRACE = 'mst'

TRACKER_NAME = 'tracker_name'
TIME = RESPONSE_TIME = 'time'
CHILD_OVERHEAD = 'child_overhead'
CHILD_TRACKER_COUNT = 'child_tracker_count'
PROCESS_ID = 'processid'

arh_connect = '/arh/connect'
arh_data = '/arh/data'
arh_trace = '/arh/trace'
webtxn_prefix = 'transaction/http'
webtxn_type = 1
bgtxn_prefix = 'transaction/bckgrnd'
bgtxn_type = 0
default_exp_status_port = 20021
default_exp_data_port = 20022
default_app_monitor_name = 'Python-Application'
default_app_port = 8080

aws_url = 'http://169.254.169.254/latest/meta-data/instance-id'
azure_url = 'http://169.254.169.254/metadata/v1/InstanceInfo'

instanceinfo = 'instance-info'
responsecode = 'response-code'
instanceid = 'instanceid'
collectorinfo = 'collector-info'

manage_agent = 911
license_expired = 701
license_instance_exceeded = 702
instance_add_failed = 703
delete_agent = 900
invalid_agent = 901
unmanage_agent = 910
agent_license_updated = 915
agent_config_updated = 920
shutdown = 0

LOG_FILE_MODE = 'a'
DEFAULT_LOG_FILE_SIZE = 5*1024*1024
DEFAULT_LOG_FILE_BACKUP_COUNT = 10
LOG_FILE_ENCODEING = None
LOG_FILE_DELAY = 0

conf_file_name = 'apminsight_conf.json'
info_file_name = 'apminsight.json'
base_dir = 'apminsightdata'
logs_dir = 'logs'
log_name = 'apminsight-agent-log.txt'
agent_logger_name = 'apminsight-agent'
log_format = '%(asctime)s %(processid)s %(levelname)s %(message)s'
AGENT_CONFIG_INFO_FILE_NAME = 'apminsight_info.json'

license_key_env = 'S247_LICENSE_KEY'
apm_app_name = 'APM_APP_NAME'
apm_app_port = 'APM_APP_PORT'
apm_print_payload = 'APM_PRINT_PAYLOAD'
apm_collector_host = 'APM_COLLECTOR_HOST'
apm_collector_port = 'APM_COLLECTOR_PORT'
apm_proxy = 'APM_PROXY'
apm_logs_dir = 'APM_LOGS_DIR'
ssl_port = '443'
APM_EXP_HOST = 'APM_EXPORTER_HOST'
APM_EXP_STATUS_PORT = 'APM_EXPORTER_STATUS_PORT'
APM_EXP_DATA_PORT = 'APM_EXPORTER_DATA_PORT'
APM_LOG_FILE_SIZE = 'APM_LOG_FILE_SIZE'
APM_LOG_FILE_BACKUP_COUNT  = 'APM_LOG_FILE_COUNT'
PROCESS_CPU_THRESHOLD = "APM_PROCESS_CPU_THRESHOLD"
PROCESS_CPU_THRESHOLD_VAL = 60.0

us_collector_host = 'plusinsight.site24x7.com' 
eu_collector_host = 'plusinsight.site24x7.eu' 
cn_collector_host = 'plusinsight.site24x7.cn'
ind_collector_host = 'plusinsight.site24x7.in'
aus_collector_host = 'plusinsight.site24x7.net.au'
jp_collector_host = 'plusinsight.site24x7.jp'

custom_config_info = 'custom_config_info'
agent_specific_info = 'agent_specific_info'
log_level = 'apminsight.log.level'
apdexth = 'apdex.threshold'
sql_capture = 'sql.capture.enabled'
sql_parametrize = 'transaction.trace.sql.parametrize'
last_modified_time = 'last.modified.time'
trace_threshold = 'transaction.trace.threshold'
trace_enabled = 'transaction.trace.enabled'
sql_stacktrace = 'transaction.trace.sql.stacktrace.threshold'
web_rum_appkey = 'webtransaction.rum.key'
webtxn_naming_use_requesturl = 'webtransaction.naming.use.requesturl'
web_txn_sampling_factor = 'transaction.tracking.request.interval'
auto_upgrade = 'autoupgrade.enabled'
txn_skip_listening = 'transaction.skip.listening'
txn_tracker_drop_th = 'webtransaction.tracker.drop.threshold'
txn_trace_ext_count_th = 'webtransaction.trace.external.components.count.threshold'


bgtxn_tracking_enabled = 'bgtransaction.tracking.enabled'
bgtxn_trace_enabled = 'bgtransaction.trace.enabled'
bgtxn_traceth = 'bgtransaction.trace.threshold'
bgtxn_sampling_factor = 'bgtransaction.tracking.request.interval'

LICENSE_KEY_FOR_DT_REQUEST = 'S247-license'
LICENSE_KEY_FOR_DT_REQUEST_HTTP = 'HTTP_S247_LICENSE'
DT_LK_KEY = 'DT_LK_KEY'
DTDATA = 'dtdata'
DT_TXN_NAME = 't_name'
DT_ST_TIME = 's_time'
DT_INS_ID = 'instance_id'

apdex_metric = 'metricstore.metric.bucket.size'
db_metric = 'metricstore.dbmetric.bucket'
bg_metric = 'metricstore.bgmetric.bucket.size'
trace_size = 'transaction.tracestore.size'

select_query_matcher = r'\s*(select)\s+.*from\s+(\S+)?.*'
insert_query_matcher = r'\s*(insert)\s+into\s+(\S+)?[(]?.*'
update_query_matcher = r'\s*(update)\s+(\S+)?.*'
delete_query_matcher = r'\s*(delete)\s+.*from\s+(\S+)?.*'
create_query_matcher = r'\s*(create)\s+(?:table|procedure|database|keyspace)\s+(?:if not exists\s+)?(\S+)?[(]?.*'
drop_query_matcher = r'\s*(drop)\s+(?:table|procedure|database|keyspace)\s+(?:if exists\s+)?(\S+)?.*'
alter_query_matcher = r'\s*(alter)\s+(?:table|procedure|database|keyspace)\s+(\S+)?.*'
call_sp_matcher = r'\s*(call)\s+([`\w]+)[\s()]*.*'
exec_sp_matcher = r'\s*(exec)\s+([`\w]+)[\s()]*.*'
show_query_matcher = r'\s*(show)\s+(\w+)(\s+)?.*'


db_opn_regex = {
    'select' : select_query_matcher,
    'insert' : insert_query_matcher,
    'update' : update_query_matcher,
    'delete' : delete_query_matcher,
    'create' : create_query_matcher, 
    'drop' : drop_query_matcher, 
    'alter' : alter_query_matcher,
    'show' : show_query_matcher,
    'call' : call_sp_matcher,
    'exec' : exec_sp_matcher
}


max_trackers = 1000
max_exc_per_trace = 20
django_comp = 'DJANGO'
flask_comp = 'FLASK'
bottle_comp = 'BOTTLE'
pyramid_comp = 'PYRAMID'
cherrypy_comp = 'CHERRYPY'
sqlite_comp = 'SQLITE'
postgres_comp = 'POSTGRES'
mysql_comp = 'MYSQL'
redis_comp = 'REDIS'
memcache_comp = 'MEMCACHED'
middleware = 'MIDDLEWARE'
template = 'TEMPLATE'
jinja_comp = 'JINJA'
mako_comp = 'MAKO'
genshi_comp = 'GENSHI'
cassandra_comp = 'CASSANDRA'
ORACLE_DSN_FORMAT = r'(?:([^:\/]+)\/?(?:([^@]+))?@)?([^:\/]+)\:?(\d*)?\/?(.*)?'
ORACLE_DEFAULT_PORT = 1521
ORACLE_COMP = oracle_comp = "ORACLE"
pyodbc_comp = 'PYODBC'
HTTP = http_comp = 'HTTP'
MONGO_COMP = mongo_comp = "MONGODB"
python_comp = 'PYTHON'
mssql_comp = 'MSSQL'
REQUESTS = 'REQUESTS'
REQUEST_URL = 'request_url'
APM_INSTRUMENTED = "apminsight_instrumented"
fastapi_comp = "FastAPI"
starlette_comp ="STARLETTE"

int_components = [ django_comp, flask_comp, middleware, jinja_comp, mako_comp, genshi_comp, cherrypy_comp, bottle_comp, pyramid_comp, fastapi_comp, starlette_comp ]
ext_components = [ mysql_comp, redis_comp, memcache_comp, postgres_comp, cassandra_comp, http_comp, sqlite_comp, mongo_comp, oracle_comp, mssql_comp, pyodbc_comp]
