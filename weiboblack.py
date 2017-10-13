#! usr/bin/env python3
#! -*- coding:utf-8 -*-

import sys
import os

import requests
import json

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




# 微博屏蔽的接口
black_url = 'https://weibo.com/aj/filter/block?ajwvr=6'
white_url = 'https://weibo.com/aj/f/delblack?ajwvr=6'
#全局函数微博登陆session
global weibosession


#微博登陆类，继承requests.Session
class WeiboSession(requests.Session):
    def __init__(self, username, password):
        super(WeiboSession, self).__init__()
        self.__username = username
        self.__password = password

    def __del__(self):
        self.close()

    def login(self):
        loginURL = "http://passport.weibo.cn/sso/login"
        data = {
            "username": self.__username,
            "password": self.__password,
            "savestate": "1",
            "r": "http://m.weibo.cn/",
            "ec": "0",
            "entry": "mweibo",
            "mainpageflag": "1",
        }
        self.headers.update({
            "Referer": "http://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F&sudaref=passport.weibo.cn&retcode=6102",
        })
        retJson = self.post(loginURL, data=data).json()
        if retJson["retcode"] == 20000000:
            for tmpURL in retJson["data"]["crossdomainlist"].values():
                self.get(tmpURL)
            myURL = "http://weibo.cn/"
            self.get(myURL)
            print(self.get(myURL))
            print('登陆成功\n')
            lb_log_state.configure(text='已登录~！', style="YH10blue.TLabel")

def login_weibo(user, pw):
#微博登陆、定义全局session
    global weibosession
    try:
        weibosession = WeiboSession(user, pw)
        weibosession.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"})
        weibosession.login()
    except Exception as e:
        print(e)
    finally:
        pass


def txt_to_list(txt):
# 读取名单列表
    with open(txt, 'r') as f:
        lst = f.read().replace(' ','').split('\n')
        lst = [x for x in lst if x!='']
    return lst

def list_to_txt(lst, txt):
# 列表写入txt
    with open(txt, 'w') as f:
        for i in lst:
            f.write(i)
            f.write('\n')


def add_blacklist(url, lst):
# 逐个加入黑名单
    global weibosession
    black_data = {'uid': '',
                  'filter_type':'1',
                  'status':'1',
                  'interact':'1',
                  'follow':'1'}
    for uid in lst:
        black_data['uid'] = uid
        weibosession.headers['Referer'] = 'http://weibo.com/u/' + uid
        retText = weibosession.post(url, data=black_data).text
        retJson = json.loads(retText)
        print("屏蔽用户：%s 结果：%s" % (uid, retJson["msg"]))

def quit_blacklist(url, lst):
# 逐个拉出黑名单
    global weibosession
    white_data = {'uid': '',
                  'f':'1',
                  'status':'1',
                  'oid': uid,
                  'wforce':'1'}
    for uid in lst:
        white_data['uid'] = uid
        weibosession.headers['Referer'] = 'http://weibo.com/u/' + uid
        retText = weibosession.post(url, data=white_data).text
        retJson = json.loads(retText)
        print("取消屏蔽用户：%s 结果：%s" % (uid, retJson["msg"]))


def into_done(lst, txt):
#使用lst的原因，在进行屏蔽or解除操作时，已经先读取过了
    done0 = txt_to_list(txt)
    done = set(done0).union(set(lst))
    list_to_txt(done, txt)
    
def out_done(lst, txt):
#使用lst的原因，在进行屏蔽or解除操作时，已经先读取过了
    done0 = txt_to_list(txt)
    done = [x for x in done0 if x not in lst]
    list_to_txt(done, txt)
    

def blackit():
    global weibosession
    try:
        lst = txt_to_list('bin\\blacklist.txt')
        add_blacklist(black_url, lst)
        into_done(lst, 'bin\\done.txt')
        print('black done......\n')
    except Exception as e:
        print(e)
    finally:
        pass

def whiteit():
    global weibosession
    try:
        lst = txt_to_list('bin\\whitelist.txt')
        add_blacklist(white_url, lst)
        out_done(lst, 'bin\\done.txt')
        print('white done......\n')
    except Exception as e:
        print(e)
    finally:
        pass
    

def disp_info(txt):
#显示拉黑人员，并统计个数
    lst = txt_to_list(txt)
    print('\n已拉黑人员uid如下：')
    for i in lst:
        print('--'+i)
    print('>>>共计拉黑人数为： %s\n' % len(lst))



#创建窗体GUI
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
style.configure("YH10red.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'red')
style.configure("YH10blue.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10black.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'black')

style.configure("YH10red.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'red')
style.configure("YH10blue.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10black.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'black')



lf0 = ttk.LabelFrame(win, text='微博登陆')
lf0.grid(row=1, column=1, columnspan=100, padx=10, pady=10, sticky='N')
for i in [0,10,20,30,100]:
    lf0.rowconfigure(i, minsize=10)
    lf0.columnconfigure(i, minsize=10)

lb_log_state = ttk.Label(lf0, text='未登录……', style="YH10red.TLabel")
lb_log_state.grid(row=1, column=5, columnspan=30, sticky='N')
ttk.Label(lf0, text='用户名：').grid(
    row=11, column=11, sticky='E')
entry_username = ttk.Entry(lf0, width=30)
entry_username.grid(row=11, column=21, sticky='W')
ttk.Label(lf0, text='密码：').grid(
    row=21, column=11, sticky='E')
entry_password = ttk.Entry(lf0, width=30)
entry_password.grid(row=21, column=21, sticky='W')

bt_login = ttk.Button(lf0, text=' 登  陆 ', width=10,
                      command=lambda:login_weibo(entry_username.get(),
                                                 entry_password.get()),
                      style='YH10black.TButton')
bt_login.grid(row=31, column=5, columnspan=30, sticky='N')


lf1 = ttk.LabelFrame(win, text='功能操作')
lf1.grid(row=11, column=1, columnspan=100, padx=10, pady=10, sticky='N')
for i in [0,10,20,100]:
    lf1.rowconfigure(i, minsize=10)
    lf1.columnconfigure(i, minsize=10)
    
bt_black = ttk.Button(lf1, text='黑名单 修改', width=25,
                      command=lambda:os.startfile('bin\\blacklist.txt', 'open'),
                      style='YH10red.TButton')
bt_black.grid(row=1, column=1, sticky='N')
bt_blackit = ttk.Button(lf1, text='加入黑名单！', width=25,
                        command=blackit, style='YH10red.TButton')
bt_blackit.grid(row=1, column=21, sticky='N')

bt_white = ttk.Button(lf1, text='白名单 修改', width=25,
                      command=lambda:os.startfile('bin\\whitelist.txt', 'open'),
                      style='YH10blue.TButton')
bt_white.grid(row=11, column=1, sticky='N')
bt_blackit = ttk.Button(lf1, text='拉出黑名单……', width=25,
                        command=whiteit, style='YH10blue.TButton')
bt_blackit.grid(row=11, column=21, sticky='N')

bt_white = ttk.Button(lf1, text='查看已拉黑名单文件', width=25,
                      command=lambda:os.startfile('bin\\done.txt', 'open'),
                      style='YH10blue.TButton')
bt_white.grid(row=21, column=1, sticky='N')
bt_blackit = ttk.Button(lf1, text='列出已拉黑人员（及个数）', width=25,
                        command=lambda:disp_info('bin\\done.txt'),
                        style='YH10blue.TButton')
bt_blackit.grid(row=21, column=21, sticky='N')



win.mainloop()
