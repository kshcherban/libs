#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class Daemon:
    """Simple class that allows to daemonize python script"""
    def __init__(self, pidfile='/tmp/daemon.pid', stdin='/dev/null',
            stdout='/dev/null', stderr='/dev/null'):
        """Takes pidfile, stdin, stdout (log), stderr as parameters"""
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """Fork from parent"""
        if os.fork():
            os._exit(0)
        os.setsid()
        # Redirect standard file descriptors
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), 0)
        os.dup2(so.fileno(), 1)
        os.dup2(se.fileno(), 2)
        # Write pidfile
        try:
            os.remove(self.pidfile)
        except:
            pass
        # Get current process id
        pid = str(os.getpid())
        # Write it to pidfile
        file(self.pidfile,'w+').write('%s\n' % pid)

    def start(self):
        """Start the daemon, returns False if pidfile exists"""
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        if pid:
            print 'pidfile %s already exist. Daemon already running?' % (self.pidfile)
            return False
        print 'Daemon started'
        self.daemonize()

    def status(self):
        """Get status of the daemon, returns True if daemon running,
        False if daemon stopped"""
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            print 'Daemon stopped'
            return False
        if pid:
            try:
                os.kill(pid, 0)
                print 'Daemon running. Pid: %s' % (pid)
                return True
            except OSError, err:
                print 'pidfile %s already exist but process is dead' % (self.pidfile)
                print '%s %s' % (err, pid)
                return False

    def stop(self):
        """Stop the daemon, returns False if no pidfile or error, True if stopped"""
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        if not pid:
            print 'pidfile %s does not exist. Daemon not running?' % (self.pidfile)
            return False
        try:
        # Killing with default SIGTERM
            while 1:
                os.kill(pid, 15)
                time.sleep(0.1)
                print 'Daemon stopped'
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                return False

    def restart(self):
        """Restart the daemon"""
        self.stop()
        self.start()

