from flask import Flask, Response
import gevent
import subprocess, os, signal
import json
import time
import datetime

app = Flask(__name__)
_LOGFILE_PATH = '/log/' + str(datetime.date.today()) + '.log'

def _save_log(_row:str, _path:str):
    with open(file=_path, mode='a') as file:
        file.write(_row)
        
def _get_child_processes_pid(parent_pid, sig=signal.SIGTERM):
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    return ps_output

@app.route("/")
def gevent_tester():
    _parent_pid = os.getppid()
    ps_output = _get_child_processes_pid(parent_pid=_parent_pid)
    _save_text = "hello, " + str((ps_output.strip()).decode('utf-8')) + "  \n"
    _save_log(_row=_save_text, _path=_LOGFILE_PATH)
    # time.sleep(2)
    gevent.sleep(2)
    _headers = {
        'Access-Control-Allow-Origin' : '*',
        'Content-Type' : 'application/json'
    }
    return Response({ _save_text}, headers=_headers)

if __name__ == '__main__':
    app.run(debug=True)
