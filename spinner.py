#!/usr/bin/env python
# vim:fileencoding=utf8

# Spinner.py
# Most of this is written by Pádraig Brady and
# licensed under CC-BY-SA
# Can be found at http://www.pixelbeat.org/talks/python/spinner.py
# The rest is written by Tor Erling H. Opsahl and is under the same license
import os
import time
import thread
import sys

# Both python and vim understand the above encoding declaration
# If viewing this on the web, ensure you are viewing with UTF-8 character encoding

#spinner="|/-\\"
#spinner=".o0O0o. "
#spinner="⇐⇖⇑⇗⇒⇘⇓⇙" #utf8
spinner="◓◑◒◐" #utf8
#spinner="○◔◑◕●" #utf8
#spinner="◴◷◶◵" #utf8
# Note the following 2 look fine with misc fixed font,
# but under bitstream vera mono at least the characters
# vary between single and double width?
#spinner="▏▎▍▌▋▊▉█▉▊▌▍▎" #utf8
#spinner="▁▂▃▄▅▆▇█▇▆▅▄▃▂" #utf8

#convert the utf8 spinner string to a list
chars=[c.encode("utf-8") for c in unicode(spinner,"utf-8")]

def spin():
    pos=0
    while 1:
        sys.stdout.write("\r"+chars[pos])
        sys.stdout.flush()
        time.sleep(.15)
        pos+=1
        pos%=len(chars)

def cursor_visible():
    if os.uname()[0].lower()=="linux":
        os.system("tput cvvis")
def cursor_invisible():
    if os.uname()[0].lower()=="linux":
        os.system("tput civis")

# exit cleanly on Ctrl-C,
# while treating other exceptions as before.
def clean_exit():
    cursor_visible()
    sys.stdout.write("\n")
def cli_exception(type, value, tb):
    if not issubclass(type, KeyboardInterrupt):
        sys.__excepthook__(type, value, tb)
    else:
        clean_exit()
if sys.stdin.isatty():
    sys.excepthook=cli_exception

def spinner():
    cursor_invisible()
    spin()
    clean_exit()

def task():
    time.sleep(5)

if __name__ == '__main__':
    thread.start_new_thread(spinner, ())
    # as soon as task finishes (and so the program)
    # spinner will be gone as well
    task()
