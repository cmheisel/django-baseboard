# autoreloading launcher
# stolen a lot from Ian Bicking's WSGIKit (www.wsgikit.org)

import os
import sys
import time
import thread

RUN_RELOADER = True
reloadFiles = []
    
def reloader_thread():
    mtimes = {}
    while RUN_RELOADER:
        for filename in filter(lambda v: v, map(lambda m: getattr(m, "__file__", None), sys.modules.values())) + reloadFiles:
            if filename.endswith(".pyc"):
                filename = filename[:-1]
            mtime = os.stat(filename).st_mtime
            if filename not in mtimes:
                mtimes[filename] = mtime
                continue
            if mtime > mtimes[filename]:
                sys.exit(3) # force reload
        time.sleep(1)

def restart_with_reloader():
    while True:
        args = [sys.executable] + sys.argv
        if sys.platform == "win32": args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ["RUN_MAIN"] = 'true'
        exit_code = os.spawnve(os.P_WAIT, sys.executable,
                               args, new_environ)
        if exit_code != 3:
            return exit_code
        
def main(main_func):
    if os.environ.get("RUN_MAIN") == "true":
        
        thread.start_new_thread(main_func, ())

        try:
            reloader_thread()
        except KeyboardInterrupt:
            pass
    else:
        try:
            sys.exit(restart_with_reloader())
        except KeyboardInterrupt:
            sys.exit(0)
