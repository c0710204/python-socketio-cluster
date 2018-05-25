import subprocess
import sys
import os
import sys,fcntl,termios,struct
from time import sleep
try:
    import libtmux
except :
    libtmux=None
import curses
def get_env_row_col():
    data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
    return struct.unpack('hh',data)
    
class curwin(object):
    def __init__(self):
        self.buff=[]
        self.subwins=[]
        self.top=2
        self.left=2
        self.right=2
        self.bottom=2
        self.weight_lock=False
        self.height_lock=False
        self.weight=-1
        self.height=-1
        self.win = curses.newwin(2, 2, self.top, self.left)
        self.resize()
        pass
    def resize(self):
        
        c_r=get_env_row_col()
        col=c_r[1]
        row=c_r[0]
        if not self.weight_lock:
            self.weight=col-self.right-self.left
        if not self.height_lock:
            self.height=row-self.top-self.bottom
        try:
            
            self.win.resize(self.height,self.weight)
            self.win.mvwin(self.top,self.left)
        except:
            pass

    def draw(self):
        self.resize()
        i=0 
        for line in self.buff[-self.height:]:
            if len(line)>self.weight:
                line=line[0:self.weight]
            self.win.addstr(i, 0, line)
            i=i+1
        self.win.refresh()
        pass
    def setbuff(self,l):
        self.buff=l
class cur_clock(curwin):
    def __init__(self):
        super(cur_clock, self).__init__()
        self.weight=2
        self.height=2
        self.height_lock=True
        self.weight_lock=True
        self.c=0

    def draw(self):
        self.c=self.c+1
        l=['-','\\','|','/']
        self.buff=[l[self.c%4],]
        super(cur_clock, self).draw()

def main():
    #init curses
    
    
    if len(sys.argv)>1:
        target=sys.argv[1]
        autorestart=9999999
        
        if len(sys.argv)>2:
            autorestart=sys.argv[2]
        if libtmux:
            stdscr = curses.initscr()
            #stdscr.noecho()
            #stdscr.cbreak()
            stdscr.keypad(1)


            win = curwin()
            win.left=5

            sign = cur_clock()
            sign.left=3
            sign.top=1
            
            print("processing tmux subprocess...\n")
            server = libtmux.Server()
            if server.find_where({ "session_name": "pspnet" }):   
                session= server.find_where({ "session_name": "pspnet" })
            else:
                session=server.new_session(session_name="pspnet")
                
            clock=0
            try:  
                while (True):
                    if session.find_where({ "window_name": "supervisor-target" }):
                        window_target=session.find_where({ "window_name": "supervisor-target" })
                        # while session.find_where({ "window_name": "supervisor-target" }):
                        #     print("killing old window...\n")
                        #     window_old=session.find_where({ "window_name": "supervisor-target" })
                        #     window_old.kill_window()
                    else:
                        window_target=session.new_window(window_name="supervisor-target",attach=False,window_shell="python {0}".format(target))
                        window_target.set_window_option("history-limit","10000")
                        window_target.set_window_option("aggressive-resize","off")
                        window_target.set_window_option("force-width","{}".format(get_env_row_col()[1]-2))
                        window_target.set_window_option("force-height","{}".format(get_env_row_col()[0]-2))

                    panel_target=window_target.list_panes()[0]
                    while (True):
                        try:
                            window_target.set_window_option("force-width","{}".format(get_env_row_col()[1]-2))
                            window_target.set_window_option("force-height","{}".format(get_env_row_col()[0]-2))
                            if not session.find_where({ "window_name": "supervisor-target" }):
                                break
                            
                            buff=panel_target.cmd('capture-pane', '-p').stdout
                            buff.append("[{0}]".format(get_env_row_col()))
                            win.setbuff(buff)
                            win.draw()
                            sign.draw()
                        except Exception as e:
                            #raise e
                            print(e)
                            break
                    #wait window close
            except Exception as e:
                #raise e
                pass
            finally:
                curses.endwin()
        else:
            print("processing normal subprocess...\n")
            while (True):
                try:
                    ret = subprocess.call("python {0}".format(target), shell=True)
                    print("restarting....\n")
                except Exception as e:
                    print(e)
                    break
if __name__ == '__main__':
    main()
