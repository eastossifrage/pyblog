# Pyblog —— 喜欢Markdown，爱上Pyblog!

> Pyblog 是一个简单易用的在线 Markdown 博客系统，它使用 Python 的 flask 架构，理论上支持所有 flask-sqlalchemy 所能支持的数据库。博客的内容全部是 Markdown 格式，你只需要将写好的 Markdown文件的内容提交即可。同时支持多说评论，百度统计，代码高亮等常用功能。

## 用法
### 应用环境介绍
- 支持 Linux 系统，本程序默认为 Ubuntu 14.04 - 16.04 系统。
- 默认的python， 2.7.6 - 2.7.11+。
- Ubuntu 系统默认安装的nginx。
- 默认使用系统自带的 sqlite 数据库。

### 文件组织架构

```bash
gyblog/
    app/
    blog/
    config.py
    manage.py
```

### 安装 flask 的虚拟环境

```bash
$ sudo apt-get install python-virtualenv
$ cd gyblog #可以自定义目录的命名
$ virtualenv flask
$ source flask/bin/activate
(flask)$
(flask)$ pip install -r requirements.txt
```
### 安装 uWSGI
```bash
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential python python-dev
sudo pip install uwsgi
```

### 配置 nginx

```bash
sudo vi /etc/nginx/sites-available/default
```

#### 设置nginx用户组
修改nginx配置`/etc/nginx/nginx.conf`的启动用户

```bash
第1行 user os373  #最好是系统的当前用户
```

#### 新增一下内容：

```bash

server {
        listen 80;
        server_name os373.cn; # 自己的网站域名
        charset utf-8;
        client_max_body_size 75M;

        location / {
                try_files $uri @pyblog;
        }
        locahion @pyblog {
                include uwsgi_params;
                uwsgi_pass unix:/var/www/pyblog/pyblog_uwsgi.sock;
        }
}
```

### 配置 uWSGI

### 设置进程用户权限
同时，最后一行说明用来运行守护进程的用户是os373。为简单起见，将这个用户设置成应用和日志文件夹的所有者。
#### 设置用户组

```bash
sudo mkdir /var/log/uwsgi
sudo chown -R os373:os373 /var/www/pyblog/
sudo chown -R os373:os373 /var/log/uwsgi/
```
#### uWSGI配置文件
创建一个新的uWSGI配置文件/var/www/pyblog/pyblog_uwsgi.ini

```bash
[uwsgi]
base = /var/www/pyblog
app = manage
module = %(app)

home = %(base)/flask
pythonpath = %(base)
socket = /var/www/pyblog/%n.sock
master = true
processes = 8
workers = 2
chmod-socket = 644
callable = app
logto = /var/log/uwsgi/%n.log

```

执行uWSGI，用新创建的配置文件作为参数：

```bash
uwsgi --ini /var/www/pybolg/pyblog_uwsgi.ini
```

我们的工作现在基本完成了，唯一剩下的事情是配置uWSGI在后台运行，这是uWSGI Emperor的职责。

### uWSGI Emperor

创建一个初始配置来运行emperor - `sudo vi /etc/init/uwsgi.conf`：

```bash
description "uWSGI"
start on runlevel [2345]
stop on runlevel [06]
respawn
 
env UWSGI=/usr/local/bin/uwsgi
env LOGTO=/var/log/uwsgi/emperor.log
 
exec $UWSGI --master --emperor /etc/uwsgi/vassals --die-on-term --uid os373 --gid os373 --logto $LOGTO
```

最后一行运行uWSGI守护进程并让它到/etc/uwsgi/vassals文件夹查找配置文件。创建这个文件夹，在其中建立一个到链到我们刚创建配置文件的符号链接。

```bash
sudo mkdir /etc/uwsgi && sudo mkdir /etc/uwsgi/vassals
sudo ln -s /var/www/pyblog/pyblog_uwsgi.ini /etc/uwsgi/vassals
```

现在，flask应用就应该配置完成了。你可以查看`/var/log/uwsgi/`文件夹下的access.log和error.log内容，并根据提示来判断程序是否正常运行。

