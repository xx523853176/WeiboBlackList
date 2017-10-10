#! usr/bin/env python3
#! -*- coding:utf-8 -*-

import sys
import os

from urllib import request, parse
import re
from tkinter import *
import tkinter as tk
from tkinter import ttk


#由于tkinter中没有ToolTip功能，所以自定义这个功能如下
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() - 60
        y = y + cy + self.widget.winfo_rooty() + 40
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      wraplength=180)
        label.pack(ipadx=1)
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()        
#====================
def createToolTip( widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def read_header(txt):
# 加载 HTTP 请求设置
    with open(txt, 'rb') as f:
        s = f.read().decode('utf-8')
        s = s.strip().split('\n')
        url = re.findall(r'http\S+', s[0])[0]
        headers = dict()
        for k in range(2, len(s) - 2):
            ss = s[k]
            idx = ss.index(':')
            headers[ss[0:idx].strip()] = ss[(idx + 1):].strip()
    return url, headers

def read_list(txt):
# 读取名单列表
    with open(txt) as f:
        lst = f.read().strip().split('\n')
    return lst

def add_blacklist(url, headers, lst):
# 逐个加入黑名单
    for uid in lst:
        print(uid)
        req = request.Request(url, headers=headers)
        data = {'uid': uid, 'filter_type':'1', 'status':'1',
                'interact':'1', 'follow':'1'}
        f = request.urlopen(req, data=parse.urlencode(data).encode('utf8'))
        f.close()

def quit_blacklist(url, headers, lst):
# 逐个拉出黑名单
    for uid in lst:
        print(uid)
        req = request.Request(url, headers=headers)
        data = {'uid': uid, 'f':'1', 'status':'1', 'oid': uid, 'wforce':'1'}
        f = request.urlopen(req, data=parse.urlencode(data).encode('utf-8'))
        f.close()

def blackit():
    url, headers = read_header('bin\\blackhttp.txt')
    lst = read_list('bin\\blacklist.txt')
    add_blacklist(url, headers, lst)
    print('black done...')

def whiteit():
    url, headers = read_header('bin\\whitehttp.txt')
    lst = read_list('bin\\whitelist.txt')
    quit_blacklist(url, headers, lst)
    print('white done...')

win = tk.Tk()
win.title('微博黑名单工具-v1.0.20171011')
'''
#设置窗体大小
cur_width = 450#宽
cur_height = 100#高
win.maxsize(cur_width, cur_height)
win.minsize(cur_width, cur_height)
'''

#模块字体风格
style = ttk.Style()
style.configure("BW.TLabel", font=("Times", "9",'bold'))
style.configure("YH10yellow.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'orange')
style.configure("YH10purple.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'purple')
style.configure("YH10blue.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10black.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'black')
style.configure("YH10red.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'red')
style.configure("YH10blue.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'blue')


lf1 = ttk.LabelFrame(win, text='功能操作')
lf1.grid(row=1, column=1, columnspan=100, padx=10, pady=10, sticky='N')

for i in [0,10,20,100]:
    lf1.rowconfigure(i, minsize=10)
    lf1.columnconfigure(i, minsize=10)
    
bt_blackheader = ttk.Button(lf1, text='黑名单 header 修改', width=20,
                            command=lambda:os.startfile('bin\\blackhttp.txt', 'open'),
                            style='YH10red.TButton')
bt_blackheader.grid(row=1, column=1, sticky='N')
bt_black = ttk.Button(lf1, text='黑名单 修改', width=20,
                      command=lambda:os.startfile('bin\\blacklist.txt', 'open'),
                      style='YH10red.TButton')
bt_black.grid(row=11, column=1, sticky='N')
bt_blackit = ttk.Button(lf1, text='加入黑名单！', width=20,
                        command=blackit, style='YH10red.TButton')
bt_blackit.grid(row=21, column=1, sticky='N')

bt_whiteheader = ttk.Button(lf1, text='白名单 header 修改', width=20,
                            command=lambda:os.startfile('bin\\whitehttp.txt', 'open'),
                            style='YH10blue.TButton')
bt_whiteheader.grid(row=1, column=21, sticky='N')
bt_white = ttk.Button(lf1, text='白名单 修改', width=20,
                      command=lambda:os.startfile('bin\\whitelist.txt', 'open'),
                      style='YH10blue.TButton')
bt_white.grid(row=11, column=21, sticky='N')
bt_blackit = ttk.Button(lf1, text='拉出黑名单……', width=20,
                        command=whiteit, style='YH10blue.TButton')
bt_blackit.grid(row=21, column=21, sticky='N')




win.mainloop()
