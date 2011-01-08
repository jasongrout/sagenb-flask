#!/usr/bin/env python
import os, time
from functools import wraps, partial
from flask import Flask, url_for, render_template, request, session, redirect, g

class SageNBFlask(Flask):
    static_path = ''
    
    def __init__(self, *args, **kwds):
        Flask.__init__(self, *args, **kwds)

        from sagenb.misc.misc import DATA
        self.add_static_path('/css', os.path.join(DATA, "sage", "css"))        
        self.add_static_path('/images', os.path.join(DATA, "sage", "images"))
        self.add_static_path('/javascript/sage', os.path.join(DATA, "sage", "js"))
        self.add_static_path('/javascript', DATA)
        self.add_static_path('/java', DATA)

    def create_jinja_environment(self):
        from sagenb.notebook.template import env
        return env

    def static_view_func(self, root_path, filename):
        print root_path, filename
        from flask.helpers import send_from_directory
        return send_from_directory(root_path, filename)

    def add_static_path(self, base_url, root_path):
        self.add_url_rule(base_url + '/<path:filename>',
                          endpoint='/static'+base_url,
                          view_func=partial(self.static_view_func, root_path))

app = SageNBFlask(__name__)
app.secret_key = os.urandom(24)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if 'username' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwds)
    return wrapper

#############
# Main Page #
#############

@app.route('/')
def index():
    if 'username' in session:
        response =  redirect(url_for('home', username=session['username']))
        if 'remember' in request.args:
            response.set_cookie('nb_session_%s'%app.notebook.port,
                                expires=(time.time() + 60 * 60 * 24 * 14))
        else:
            response.set_cookie('nb_session_%s'%app.notebook.port)
        response.set_cookie('cookie_test_%s'%app.notebook.port, expires=1)
        return response

    from authentication import login
    return login()

@app.route('/home/<username>/')
@login_required
def home(username):
    if not app.notebook.user_is_admin(username) and username != session['username']:
        #XXX: Put this into a template
        return "User '%s' does not have permission to view the home page of '%s'."%(session['username'],
                                                                                    username)
    else:
        from sagenb.notebook.twist import render_worksheet_list
        import sagenb.notebook.twist as twist
        twist.notebook = app.notebook
        return render_worksheet_list(request.args, pub=False, username=session['username'])

@app.route('/home/')
@login_required
def bare_home():
    return redirect(url_for('home', username=session['username']))

################
# View imports #
################
import authentication

#############
# OLD STUFF #
#############
def init_updates():
    global save_interval, idle_interval, last_save_time, last_idle_time
    from sagenb.misc.misc import walltime

    save_interval = app.notebook.conf()['save_interval']
    idle_interval = app.notebook.conf()['idle_check_interval']
    last_save_time = walltime()
    last_idle_time = walltime()

#CLEAN THIS UP!
def start():
    import sys
    path_to_notebook = sys.argv[1].rstrip('/')
    port = 5000
    
    #############
    # OLD STUFF #
    #############
    import sagenb.notebook.notebook
    sagenb.notebook.notebook.JSMATH = True
    import sagenb.notebook.notebook as notebook

    app.notebook = notebook.load_notebook(path_to_notebook,interface="localhost",port=port,secure=False)
    SAGETEX_PATH = ""
    OPEN_MODE = False
    SID_COOKIE = str(hash(path_to_notebook))
    DIR = path_to_notebook
    init_updates()

    app.run(debug=True, port=port)

    app.notebook.save()
    print "Notebook saved!"
