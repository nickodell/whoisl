#!/usr/bin/python
from subprocess import Popen, PIPE
import sys
import time
from os.path import isfile
top = open("top10000").read().split("\n")
top = top[1:] # Skip first line - it's a comment
top = top[:1000] # top 1000 is good enough.


for site in top:
    print "Looking at", site
    if isfile("testcases/" + site):
        continue
    proc = Popen(["whois", site], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = proc.communicate()
    exit_code = proc.wait()
    if exit_code == 1 and "No match" in stdout:
        # That one doesn't exist?
        pass
    elif exit_code == 1 and (".CC" in stdout or ".TV" in stdout):
        # Hack around bug in whois
        pass
    elif exit_code == 1 and "has no whois server" in stdout:
        # To fix .fm
        pass
    elif exit_code == 2 and "yesnic" in stdout:
        # yesnic resets connection, whois doesn't like it
        pass
    elif exit_code != 0:
        print stdout
        print stderr
        sys.exit()
    open("testcases/" + site, "w").write(stdout)
    print "Waiting...",
    sys.stdout.flush()
    time.sleep(3)
