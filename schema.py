# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import os
import sqlite3, urllib2, json
import datetime, time
from threading import Timer, Thread


application = Flask(__name__)
application.config.from_object('config')


@application.template_filter('format_time')
def format_time(time_str, format_str='%Y-%m-%d %H:%M:%S'):
    if time_str <= 0 or time_str == '':
        return ''
    localtime = time.localtime(time_str)
    return time.strftime(format_str, localtime)


def goto_url(url, success_return, id, status=1):
    try:
        res = urllib2.urlopen(url)
        res_string = res.read()
        res_string = res_string[0:50]
    except urllib2.HTTPError as e:
        res_string = "HTTP ERROR! " + str(e.reason)
    except urllib2.URLError as e:
        res_string = "URL ERROR! " + str(e.reason)
    except Exception as e:
        res_string = "访问URL出错, 未知原因!"

    #print res_string

    if res_string == success_return:
        success_or_not = 1
    else:
        success_or_not = 2

    db = get_db()

    ctime = time.time()
    # write the db, record the result
    db.execute('UPDATE schema SET run_time=?, success_or_not=?,status=? WHERE id=?',
               [ctime, success_or_not, status, id])

    # write log
    db.execute('INSERT INTO schema_log(schema_id, success_or_not, res_string, run_time) VALUES (?,?,?,?)',
               [id, success_or_not, res_string, ctime])
    db.commit()


def cycle_schema(schema_time, unit, url, success_return, id):
    localtime = time.localtime(time.time())
    if unit == 1:
        tm = time.strftime('%M', localtime)

    elif unit == 2:
        tm = time.strftime('%H%M', localtime)

    elif unit == 3:
        tm = time.strftime('%w%H%M', localtime)

    elif unit == 4:
        tm = time.strftime('%d%H%M', localtime)

    elif unit == 5:
        tm = time.strftime('%m%d%H%M', localtime)

    else:
        return

    if int(tm) == int(schema_time):
        # print int(tm), int(schema_time)
        goto_url(url, success_return, id)


def onetime_schema(schema_time, url, success_return, id):
    localtime = time.localtime(time.time())
    tm = time.strftime('%Y%m%d%H%M', localtime)
    if int(tm) == int(schema_time):
        goto_url(url, success_return, id, 3)


def get_schema():
    with application.app_context():
        db = get_db()

        schema_list = db.execute("SELECT * FROM schema WHERE status=1 AND (strftime('%s','now')-60)>run_time")

        for list in schema_list:
            if list['type'] == 1:  # 固定时间循环执
                cycle_schema(list['schema_time'], list['unit'], list['url'], list['success_return'], list['id'])
            elif list['type'] == 2:  # 固定时间执行一次
                onetime_schema(list['schema_time'], list['url'], list['success_return'], list['id'])

        print "------ %s  ------" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


@application.route('/schema_log_list', methods=['GET'])
def schma_log_list():
    db = get_db()
    schema_id = request.args.get('schema_id')
    cur = db.execute('SELECT * FROM schema_log WHERE schema_id=? ORDER BY id DESC ', [schema_id])
    schema_log_list = cur.fetchall()
    return render_template('schema_log_list.html', schema_log_list=schema_log_list)


@application.route('/schema_list')
def schema_list():
    db = get_db()
    cur = db.execute('SELECT * FROM schema ORDER BY id DESC ')
    schema_list = cur.fetchall()
    return render_template('schema_list.html', schema_list=schema_list)


@application.route('/edit', methods=['GET', 'POST'])
def edit():
    """if not session.get('logged_in'):
            abort(401)
    """

    db = get_db()
    if request.method != 'POST':
        id = request.args.get('id')
        cur = db.execute('SELECT * FROM schema WHERE id=?', [id])
        schema_detail = cur.fetchone()
        return render_template('edit.html', schema_detail=schema_detail)

    # if post
    id             = int(request.form.get('id', 0))
    title          = request.form.get('title', '')
    type           = int(request.form.get('type', 0))
    unit           = int(request.form.get('unit', 0))
    schema_time    = request.form.get('schema_time', 0)
    url            = request.form.get('url', '')
    success_return = request.form.get('success_return', '')
    text           = request.form.get('text', '')
    status         = int(request.form.get('status', 0))

    result = {'status': 0, 'info': '未定义错误','data': ''}

    if title == '':
        result['info'] = "标题不能为空"
        return result

    if url == '':
        result['info'] = "URL不能为空"
        return result

    if success_return == '':
        result['info'] = "执行成功返回值不能为空"
        return result

    if type < 1 or type > 3:
        result['info'] = "任务类型不正确"
        return result

    if type == 2:
        if unit < 1 or unit > 5:
            result['info'] = "请选择规划的类型"
            return result

    if schema_time == 0:
        result['info'] = "时间不能为空"
        return result

    if status < 1 or status > 2:
        result['info'] = "启用状态不能为空"
        return result

    if id > 0:
        db.execute('UPDATE schema SET title=?, url=?, text=?, success_return=?, type=?, unit=?, schema_time=?, status=?, add_time=? WHERE id=?',
            [title, url, text, success_return, type, unit, schema_time, status, time.time(), id])
    else:
        db.execute('INSERT INTO schema(title, url, text, success_return, type, unit, schema_time, status, add_time) VALUES (?,?,?,?,?,?,?,?,?)',
                   [title, url, text, success_return, type, unit, schema_time, status, time.time()])

    db.commit()
    # flash('New entry was successfully posted')
    result = {'status': 1, 'info': '保存成功', 'data': ''}
    return json.dumps(result)


@application.route("/delete", methods=['GET'])
def delete():
    id = request.args.get('id')

    if id <= 0:
        return json.dumps({'status': 0, 'info': '参数错误, id丢失', 'data': ''})

    db = get_db()
    db.execute('DELETE FROM schema WHERE id=?', [id])
    db.commit()

    return json.dumps({'status': 1, 'info': '删除成功', 'data': ''})

# Load default config and override config from an environment variable
application.config.update(dict(
    DATABASE=os.path.join(application.root_path, 'schema.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
application.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(application.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@application.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None


if __name__ == '__main__':
    scheduler = Scheduler(40, get_schema)
    scheduler.start()
    application.run(host='0.0.0.0')
    scheduler.stop()
