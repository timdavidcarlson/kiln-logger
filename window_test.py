from tkinter import *
import datetime
import threading
import time

root = Tk()
root.title("Thread Test")
#print('Main Thread', threading.get_ident())    # main thread id

def timecnt():  # runs in background thread
    print('Timer Thread',threading.get_ident())  # background thread id
    for x in range(100):
        root.event_generate("<<event1>>", when="tail", state=123) # trigger event in main thread
        txtvar.set(' '*15 + str(x))  # update text entry from background thread
        time.sleep(1.25)  # one quarter second

def eventhandler(evt):  # runs in main thread
    print('Event Thread',threading.get_ident())   # event thread id (same as main)
    print(evt.state)  # 123, data from event
    string = datetime.datetime.now().strftime('%I:%M:%S %p')
    lbl.config(text=string)  # update widget
    #txtvar.set(' '*15 + str(evt.state))  # update text entry in main thread

lbl = Label(root, text='Start')  # label in main thread
lbl.place(x=0, y=0, relwidth=1, relheight=.5)

txtvar = StringVar() # var for text entry
txt = Entry(root, textvariable=txtvar)  # in main thread
txt.place(relx = 0.5, rely = 0.75, relwidth=.5, anchor = CENTER)

thd = threading.Thread(target=timecnt)   # timer thread
thd.daemon = True
thd.start()  # start timer loop

root.bind("<<event1>>", eventhandler)  # event triggered by background thread
root.mainloop()
thd.join()  # not needed

exit()