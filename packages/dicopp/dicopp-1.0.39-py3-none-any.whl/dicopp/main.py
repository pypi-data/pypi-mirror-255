import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk,GLib

import os
import sys

from . import base
from . import layout 
from . import limit
from . import log
from . import stor2
from . import nick
from . import hubs
from . import hubscon
from . import daem
from . import search
from . import dload
from . import com
from . import first

def quit(widget, mainloop):
	base.write(widget)
	daem.close(False)#in base.write is log, can require daemon open
	limit.close()
	hubscon.close()
	search.close()
	dload.close()
	com.close()
	mainloop.quit()
	return True

def main():
	if len(sys.argv)>1:
		cleanup()
		return
	first.ini()
	mainloop = GLib.MainLoop()
	win = Gtk.Window()
	win.set_title('Direct Connect')
	d=base.read(win)
	layout.show(win)
	limit.open(win)
	log.ini()
	stor2.ini()
	nick.ini(False)
	hubs.ini()
	win.connect('close-request', quit, mainloop)
	try:
		daem.dopen()
	except Exception:
		print("daemon open error")
		return
	base.read2(d)#after daemon start
	win.show()
	mainloop.run()

def cleanup():
	#remove config and exit
	c=base.get_client_dir()
	if os.path.isdir(c):
		print("Would remove:");
		f=base.get_client()
		if os.path.isfile(f):
			print(f)
		else:
			f=None
		print(c)
		print("yes ?");
		str = ""
		while True:
			x = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
			if x == '\n':
				break
			str += x
		if str=="yes":
			r=" removed"
			if f:
				os.remove(f)
				print(f+r)
			if len(os.listdir(path=c))==0:
				os.rmdir(c) #OSError if not empty
				print(c.__str__()+r)
			else:
				print(c.__str__()+" is not empty.")
		else:
			print("expecting \"yes\"")

if __name__ == "__main__":
    main()
