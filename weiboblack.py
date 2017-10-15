#! usr/bin/env python3
#! -*- coding:utf-8 -*-

import sys
import os
import time

import requests
import json
import webbrowser
import random

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

#版本号：
version = 'v1.2.20171015'

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



########################################
########################################
# 微博屏蔽的接口
black_url = 'https://weibo.com/aj/filter/block?ajwvr=6'
white_url = 'https://weibo.com/aj/f/delblack?ajwvr=6'
#全局函数微博登陆session
global weibosession
#全局函数，发包时间
global mintime
global maxtime
    

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
            bt_login.configure(state='disable')

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
        time.sleep( random.uniform(mintime,maxtime) )

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
        time.sleep( random.uniform(mintime,maxtime) )


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


########################################
########################################
#创建窗体GUI
win = tk.Tk()
win.title('微博黑名单工具-'+version)

#设置窗体大小
cur_width = 435#宽
cur_height = 600#高
win.maxsize(cur_width, cur_height)
win.minsize(cur_width, cur_height)



#模块字体风格
style = ttk.Style()
style.configure("BW.TLabel", font=("Times", "9",'bold'))
style.configure("YH10red.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'red')
style.configure("YH10blue.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10grey.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'grey')
style.configure("YH10black.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'black')

style.configure("YH10info.TLabel", font=("微软雅黑", "9",), foreground  = 'black')
style.configure("YH10url.TLabel", font=("微软雅黑", "9",), foreground  = 'blue')
style.configure("YH10infoblue.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10infored.TLabel", font=("微软雅黑", "9",'bold'), foreground  = 'red')

style.configure("YH10red.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'red')
style.configure("YH10blue.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'blue')
style.configure("YH10orange.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'orange')
style.configure("YH10black.TButton", font=("微软雅黑", "9",'bold'), foreground  = 'black')


########################################
########################################
lf0 = ttk.LabelFrame(win, text='微博登陆')
lf0.grid(row=1, column=1, columnspan=100, padx=10, pady=10, sticky='N')
for i in [0,10,20,30,100]:
    lf0.rowconfigure(i, minsize=10)
    lf0.columnconfigure(i, minsize=10)

lb_log_state = ttk.Label(lf0, text='未登录……', style="YH10red.TLabel")
lb_log_state.grid(row=1, column=5, columnspan=30, sticky='N')
ttk.Label(lf0, text='用户名：').grid(
    row=11, column=11, sticky='E')
entry_username = ttk.Entry(lf0, state='readonly', width=30)
entry_username.grid(row=11, column=21, sticky='W')
ttk.Label(lf0, text='密码：').grid(
    row=21, column=11, sticky='E')
entry_password = ttk.Entry(lf0, state='readonly', width=30)
entry_password.grid(row=21, column=21, sticky='W')

bt_login = ttk.Button(lf0, text=' 登  陆 ', width=10,
                      command=lambda:login_weibo(entry_username.get(),
                                                 entry_password.get()),
                      style='YH10black.TButton')
bt_login.grid(row=31, column=5, columnspan=30, sticky='N')


########################################
########################################
mintime = 1 #发包间隔最小值
maxtime = 2 #发包间隔最大值

def set_posttime(mint, maxt):
    global mintime
    global maxtime
    try:
        mintime = float(mint)
        maxtime = float(maxt)
        assert(maxtime>=mintime)
        lb_time.configure(text='当前设定： %.2f-%.2f秒间随机发送一个请求' % (mintime, maxtime))
    except Exception as e:
        messagebox.showinfo('Error',message='请检查是否输入正确！')
    finally:
        pass

lf2 = ttk.LabelFrame(win, text='参数设定')
lf2.grid(row=2, column=1, columnspan=100, padx=10, pady=10, sticky='N')
for i in [0,10,20,100]:
    lf2.rowconfigure(i, minsize=10)
    lf2.columnconfigure(i, minsize=10)
lf2.rowconfigure(12, minsize=5)
lb_time = ttk.Label(lf2, text='当前设定： 1.00-2.00秒间随机发送一个请求', style="YH10blue.TLabel")
lb_time.grid(row=1, column=5, columnspan=30, sticky='N')   
ttk.Label(lf2, text='每隔多长时间发送一个拉黑or解除数据包：（单位/秒）').grid(
    row=11, column=5, columnspan=30, sticky='N')
ttk.Label(lf2, text='  ').grid(row=13, column=12, sticky='N')
entry_mintime = ttk.Entry(lf2, width=10)
entry_mintime.grid(row=13, column=13, sticky='N')
ttk.Label(lf2, text='至').grid(row=13, column=14, sticky='N')
entry_maxtime = ttk.Entry(lf2, width=10)
entry_maxtime.grid(row=13, column=15, sticky='N')
ttk.Label(lf2, text='之间').grid(row=13, column=16, sticky='N')

set_login = ttk.Button(lf2, text=' 设  定 ', width=10,
                      command=lambda:set_posttime(entry_mintime.get(),
                                                  entry_maxtime.get()),
                      style='YH10black.TButton')
set_login.grid(row=21, column=5, columnspan=30, sticky='N')


########################################
########################################
lf9 = ttk.LabelFrame(win, text='功能操作')
lf9.grid(row=21, column=1, columnspan=100, padx=10, pady=10, sticky='N')
for i in [0,10,20,100]:
    lf9.rowconfigure(i, minsize=10)
    lf9.columnconfigure(i, minsize=10)
    
bt_black = ttk.Button(lf9, text='黑名单 修改', width=25,
                      command=lambda:os.startfile('bin\\blacklist.txt', 'open'),
                      style='YH10red.TButton')
bt_black.grid(row=1, column=1, sticky='N')
bt_blackit = ttk.Button(lf9, text='加入黑名单！', width=25,
                        command=blackit, style='YH10red.TButton')
bt_blackit.grid(row=1, column=21, sticky='N')

bt_white = ttk.Button(lf9, text='白名单 修改', width=25,
                      command=lambda:os.startfile('bin\\whitelist.txt', 'open'),
                      style='YH10blue.TButton')
bt_white.grid(row=11, column=1, sticky='N')
bt_blackit = ttk.Button(lf9, text='拉出黑名单……', width=25,
                        command=whiteit, style='YH10blue.TButton')
bt_blackit.grid(row=11, column=21, sticky='N')

bt_white = ttk.Button(lf9, text='查看已拉黑名单文件', width=25,
                      command=lambda:os.startfile('bin\\done.txt', 'open'),
                      style='YH10black.TButton')
bt_white.grid(row=21, column=1, sticky='N')
bt_blackit = ttk.Button(lf9, text='列出已拉黑人员（及个数）', width=25,
                        command=lambda:disp_info('bin\\done.txt'),
                        style='YH10black.TButton')
bt_blackit.grid(row=21, column=21, sticky='N')


########################################
########################################
def openurl_func(event):
    webbrowser.open('https://github.com/xx523853176/WeiboBlackList', new=1, autoraise=True)
    
def about():
    tl = tk.Toplevel()
    tl.title("关于……")
    tl_width = 400#宽
    tl_height = 160#高
    scnWidth,scnHeight = tl.maxsize()
    tmpcnf = '%dx%d+%d+%d'%(tl_width, tl_height,
                            (scnWidth-tl_width)/2, (scnHeight-tl_height)/2)
    tl.geometry(tmpcnf)
    
    info = ttk.LabelFrame(tl, text=' 信  息 ')
    info.grid(row=1, column=1, columnspan=100, padx=10, pady=10, sticky='N')
    for i in [0,100]:
        info.rowconfigure(i, minsize=10)
        info.columnconfigure(i, minsize=20)
        
    ttk.Label(info, text='Author:', style="YH10info.TLabel").grid(
        row=1, column=1, sticky='E')
    ttk.Label(info, text='HUSKY (xx523853176)', style="YH10info.TLabel").grid(
        row=1, column=2, sticky='W')
    ttk.Label(info, text='GITHUB:', style="YH10info.TLabel").grid(
        row=2, column=1, sticky='E')
    openurl = ttk.Label(info, text='https://github.com/xx523853176/WeiboBlackList',
                        style="YH10url.TLabel")
    openurl.grid(row=2, column=2, sticky='W')
    openurl.bind('<Double-Button-1>', openurl_func)
    ttk.Label(info, text='Version:', style="YH10info.TLabel").grid(
        row=3, column=1, sticky='E')
    ttk.Label(info, text='1.1.20171014', style="YH10info.TLabel").grid(
        row=3, column=2, sticky='W')
    
    ttk.Button(tl, text='关 闭', width=10, command=lambda:tl.destroy()).grid(
        row=2, column=1, columnspan=100, padx=10, sticky='E')
    
    
ttk.Button(win, text='关于……', style="YH10blue.TLabel", command=about).grid(
    row=31, column=1, columnspan=100, padx=10, pady=5, sticky='N')


########################################
########################################
def haveread(root):
    entry_username.configure(state='normal')
    entry_password.configure(state='normal')
    root.destroy()
    
def somehelp():
    tl = tk.Toplevel()
    tl.overrideredirect(True)
    tl_width = 490#宽
    tl_height = 300#高
    scnWidth,scnHeight = tl.maxsize()
    tmpcnf = '%dx%d+%d+%d'%(tl_width, tl_height,
                            (scnWidth-tl_width)/2, (scnHeight-tl_height)/2)
    tl.geometry(tmpcnf)
    
    info = ttk.LabelFrame(tl, text=' 看一眼！看一眼~~~ ')
    info.grid(row=1, column=1, columnspan=100, padx=10, pady=10, sticky='N')
    for i in [0,100]:
        info.rowconfigure(i, minsize=10)
        info.columnconfigure(i, minsize=20)

    ttk.Label(info, text='1、', style="YH10infoblue.TLabel").grid(row=1, column=1, sticky='NE')
    ttk.Label(info, text='若账号密码输入无误\n本程序会有数秒时间忙碌工作（即未响应）来进行登陆工作。\n"忙碌时间"视当前网络状况而定',
              wraplength=400, style="YH10infoblue.TLabel").grid(
                  row=1, column=2, sticky='W')
    ttk.Label(info, text='2、', style="YH10infored.TLabel").grid(row=2, column=1, sticky='NE')
    ttk.Label(info, text='请勿连续多次点击“登陆”按钮！！\n否则可能导致帐号被暂时锁定！！！！\n若控制台 ①无提示 / ②提示“Expecting value: line 1 column 1 (char 0)”，则为{账号or密码错误}，请检查或测试后再进行登录。',
              wraplength=400, style="YH10infored.TLabel").grid(
                  row=2, column=2, sticky='W')
    ttk.Label(info, text='3、', style="YH10blue.TLabel").grid(row=3, column=1, sticky='NE')
    ttk.Label(info, text='请求速度请勿定义过快（如0-0秒），以防被检测。请自行斟酌使用。。。毕竟点一下后台运行就行了，何必要块那1、2分钟……',
              wraplength=400, style="YH10blue.TLabel").grid(
                  row=3, column=2, sticky='W')
    ttk.Label(info, text='4、', style="YH10black.TLabel").grid(row=4, column=1, sticky='NE')
    ttk.Label(info, text='使用前请务必看完以上内容，因不了解以上问题而造成的封号等情况，概不负责',
              wraplength=400, style="YH10black.TLabel").grid(
                  row=4, column=2, sticky='W')

    ttk.Button(tl, text='已阅读', width=10, command=lambda:haveread(tl)).grid(
        row=2, column=1, columnspan=100, padx=10, sticky='E')


ttk.Button(win, text='务必【！点一下这里！】，否则无法登陆哈哈哈哈d=====(￣▽￣*)b',
           style="YH10red.TLabel", command=somehelp).grid(
               row=32, column=1, columnspan=100, padx=10, sticky='N')


########################################
########################################

win.mainloop()
