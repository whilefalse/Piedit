#!/usr/bin/env python

"""Piet IDE, written in Python. It's badass."""

import sys
import os.path
import threading
import signal
import pygtk
import gtk
import gtk.glade
import gnome
import piedit.ui
import piedit.interpreter
pygtk.require("2.0")

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"
        

class Program:
    """Class that runs the main program"""
    
    def __init__(self):
        """Loads the glade XML and creates the ui object"""
        gnome.init("Piedit", "0.1")
        gladeui = gtk.glade.XML(os.path.join('glade', 'piedit.glade'))
        ui = piedit.ui.UI(gladeui)
        
class GuiThread(threading.Thread):
    def run(self):
        gtk.main()
        
def key_interrupt(num,frame):
    print "Termieffnated"
    raise SystemExit

if __name__ == "__main__":
    signal.signal(signal.SIGINT,key_interrupt)
    program = Program()
    gtk.gdk.threads_init()
    gui_thread = GuiThread()
    gui_thread.start()