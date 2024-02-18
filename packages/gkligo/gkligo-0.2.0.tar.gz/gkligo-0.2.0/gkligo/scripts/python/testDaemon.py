#!/usr/bin/env python
"""
Usage:
  %s <action> [--pidfile=<pidfile>] [--logfile=<logfile>]
  %s (-h | --help)
  %s --version

where action is start|stop|restart

Options:
  -h --help                    Show this screen.
  --version                    Show version.
  --pidfile=<pidfile>          PID file [default: /tmp/ligo.pid]
  --logfile=<logfile>          PID file [default: /tmp/ligo.log]

E.g.:
  %s start

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt

import os
import time
import logging
import daemon
from daemon import pidfile
from gkutils.commonutils import cleanOptions, Struct
import signal
debug_p = True

def do_something(options):
    ### This does the "work" of the daemon

    logger = logging.getLogger('eg_daemon')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(options.logfile)
    fh.setLevel(logging.INFO)

    formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formatstr)

    fh.setFormatter(formatter)

    logger.addHandler(fh)

    while True:
        logger.debug("this is a DEBUG message")
        logger.info("this is an INFO message")
        logger.error("this is an ERROR message")
        time.sleep(5)


def shutdown(signum, frame):  # signum and frame are mandatory
    sys.stdout.write("Ah ballix...\n")
    sys.exit(0)

def start_daemon(options):
    ### This launches the daemon in its context

    global debug_p

    if debug_p:
        print("eg_daemon: entered run()")
        print("eg_daemon: pidf = {}    logf = {}".format(options.pidfile, options.logfile))
        print("eg_daemon: about to start daemonization")
        print(type(options.pidfile), type(options.logfile))

    out = sys.stdout
    err = sys.stderr

    ### XXX pidfile is a context
    with daemon.DaemonContext(
        working_directory='/tmp',
        umask=0o002,
        pidfile=pidfile.TimeoutPIDLockFile(options.pidfile),
        signal_map={ signal.SIGTERM: shutdown },
        stdout=out,
        stderr=err,
        ) as context:
        do_something(options)


if __name__ == "__main__":
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)


    if options.action not in ['start', 'stop', 'restart']:
        sys.stderr.write('Valid options for action are start|stop|restart\n')
        sys.exit(1)


    if os.path.exists(options.pidfile):
        with open(options.pidfile, mode='r') as f:
            pid = f.read().strip()
            print("Daemon is already running (PID = %s). Stop and restart if you want to restart it." % pid)
    else:
        start_daemon(options)

