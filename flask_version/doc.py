"""
Documentation functions

URLS to do:

###/pdf/       <-FILE->  DOC_PDF
###/doc/live/   - WorksheetFile(os.path.join(DOC, name)
###/doc/static/ - DOC/index.html
###/doc/static/reference/ <-FILE-> DOC/reference/
###/doc/reference/media/  <-FILE-> DOC_REF_MEDIA

/src/             - SourceBrowser
/src/<name>       - Source(os.path.join(SRC,name), self.username)

"""
import os
from flask import Module, url_for, render_template, request, session, redirect, g, current_app
from decorators import login_required, guest_or_login_required
from flaskext.autoindex import AutoIndex

doc = Module('flask_version.doc')

from sagenb.misc.misc import SAGE_DOC 
DOC = os.path.join(SAGE_DOC, 'output', 'html', 'en')

################
# Static paths #
################

#The static documentation paths are currently set in base.SageNBFlask.__init__

@doc.route('/doc/static/')
def docs_static_index():
    return redirect(url_for('/static/doc/static', filename='index.html'))

@doc.route('/doc/live/')
@login_required
def doc_live_base():
    return current_app.message('nothing to see.', username=g.username)

@doc.route('/doc/live/<path:filename>')
@login_required
def doc_live(filename):
    filename = os.path.join(DOC, filename)
    if filename.endswith('.html'):
        from worksheet import worksheet_file
        return worksheet_file(filename)
    else:
        from flask.helpers import send_file
        return send_file(filename)

SRC = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage')
idx = AutoIndex(doc, browse_root=SRC)

@doc.route('/src/')
@doc.route('/src/<path:path>')
@guest_or_login_required
def autoindex(path='.'):
    filename = os.path.join(SRC, path)
    if os.path.isfile(filename):
        from cgi import escape
        src = escape(open(filename).read())
        return render_template(os.path.join('html', 'source_code.html'), src_filename=path, src=src, username = g.username)
    return idx.render_autoindex(path)
