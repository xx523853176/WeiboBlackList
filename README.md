﻿# WeiboBlackList
微博批量拉黑

exe文件夹内为windows运行程序，含控制台显示进度。

list.txt中为 现有微博监督员 的 UID。


## 使用前需要：
1、下载fiddler并安装。

2、登录网页版微博，找到一个用户，准备 拉黑/取消拉黑。

3、打开 Fiddler并清空记录。

4、拉黑/取消拉黑 刚刚准备的测试用户。

5、在 Fiddler 中选中对应请求，选择 Raw 格式进行查看，并将结果复制到 “黑名单header修改”（blackhttp.txt）或 “白名单header修改”（whitehttp.txt）中。



## 建议：
随时关注更新list.txt文件，并留作备份。

方便知晓现已拉黑的人。

使用时将list.txt中的内容复制到“黑名单修改”（blacklist.txt）或“白名单修改”（whitelist.txt）中，并使用即可。



## 原说明
list.txt 中是 微博监督员 关注列表前 100 个用户的 UID。 现在微博只能查看前 5 页关注列表，所以不能获取全部 400 多个微博监督员的 UID。 

欢迎大家补充 微博监督员 的 UID 到 list.txt。网页版微博打开主页，第一串数字就是 UID。 

