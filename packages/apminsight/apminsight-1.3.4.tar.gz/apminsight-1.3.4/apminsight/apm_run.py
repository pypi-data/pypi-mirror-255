import os
import sys
import time
import argparse

debug = False

command_help ="""
command : apminisght-run <options> <user application command>
Add options and user application startup commands as arguments
Examples
apminsight-run python app.py
apminsight-run --apm_app_name "monitorname" gunicorn myproject.wsgi
apminsight-run --apm_app_name "monitorname" --apm_log_dir "logs location" gunicorn myproject.wsgi
"""

def log(text,*args):
    if debug : 
        currenttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print("APMINSIGH_PYTHON %s (%d) - %s" % (currenttime, os.getpid(), text%args))

def set_apm_config(args):
    debug = args.apm_debug or os.environ.get('APM_DEBUG', False)
    if debug:
        os.environ["APM_DEBUG"] = True
    
    if args.apm_app_name:
        os.environ["APM_APP_NAME"] = args.apm_app_name
        print(os.getenv("APM_APP_NAME"))
    if args.apm_log_dir:
        os.environ["APM_LOGS_DIR"] = args.apm_log_dir
    
    os.environ["APM_EXPORTER_HOST"] = args.apm_exp_host
    os.environ["APM_EXPORTER_STATUS_PORT"] = args.apm_exp_status_port
    os.environ["APM_EXPORTER_DATA_PORT"] =  args.apm_exp_data_port


def set_bootstrap_path(root_dir):

    bootstrap_dir = os.path.join(root_dir, 'bootstrap')
    log('boot_directory = %r', bootstrap_dir)

    python_path = os.environ.get("PYTHONPATH", "")
    if 'PYTHONPATH' in os.environ:
        python_path = "%s%s%s" % (bootstrap_dir, os.path.pathsep, os.environ['PYTHONPATH'])
    
    os.environ["PYTHONPATH"] = python_path if python_path else bootstrap_dir 
    
    log("PYTHONPATH: %s", os.environ["PYTHONPATH"])
    log("sys.path: %s", sys.path)


def get_executable_path(executable_path):
    if not os.path.dirname(executable_path):
        program_search_path = os.environ.get('PATH', '').split(os.path.pathsep)
        for path in program_search_path:
            path = os.path.join(path, executable_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                executable_path = path
                break
    return executable_path

def main():    
    global debug
    try:   
        parser = argparse.ArgumentParser(description=command_help,formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("command", nargs=argparse.REMAINDER, type=str, help="Add Application Command that need to be executed")
        parser.add_argument("-apmname","--apm_app_name", help="Add APM Insight application name")
        parser.add_argument("-ald","--apm_log_dir", help="Add custom log directory for storing APM logs ")
        parser.add_argument("-ad","--apm_debug", help="enable debug mode")
        parser.add_argument("-aeh","--apm_exp_host",help="Set apm exporter host to a remote machine or docker container host", default="localhost")
        parser.add_argument("-aesp","--apm_exp_status_port",help="Set apm exporter status port ", default="20021")
        parser.add_argument("-aedp","--apm_exp_data_port",help="Set apm exporter data port", default="20022")

        if len(sys.argv[1:]) == 0:
            print("[WARNING] Insufficient details passed to the command")
            print("For additional Info run the command apminsight-run --help")
            sys.exit(1)
            
        args = parser.parse_args()
       
        set_apm_config(args)
        
        log('current_command = %r', sys.argv)
        import apminsight
        root_dir = os.path.dirname(apminsight.__file__)
        log('root_directory = %r', root_dir)
        
        # add boothstrap to python path
        set_bootstrap_path(root_dir)

        #check the python executable is available under os.path
        executable_path= get_executable_path(args.command[0])
        executable_args = args.command[1:]
        
        log('executable_arguments = %r', [executable_path] + executable_args)

        try:
            os.execl(executable_path, executable_path, *executable_args)
        except Exception:
            print("apminsight-run: error while executing the user command '%s' %s" % (executable_path % executable_args, str(Exception)))
            raise
    except Exception:
        print("apminsight-run: Error while executing the script '%s' %s" % (sys.argv,str(Exception)))
        raise   
    
    sys.exit(0)
    

