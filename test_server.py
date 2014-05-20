import os
import json
import flask
import time
import cherrypy.wsgiserver
import spell_check

spell_check = spell_check.SpellCheck()
spell_check.read_file()

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8500))
INDEX_DATA = open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
    'index.html')).read()
app = flask.Flask('pritunl_ip')

def jsonify(data=None, status_code=None):
    if not isinstance(data, basestring):
        data = json.dumps(data)
    response = flask.Response(response=data, mimetype='application/json')
    response.headers.add('Cache-Control',
        'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    if status_code is not None:
        response.status_code = status_code
    return response

@app.route('/', methods=['GET'])
def index_get():
    return INDEX_DATA

@app.route('/check', methods=['GET'])
def check_get():
    word = flask.request.args.get('q')
    run_time, matches = spell_check.get_matches_timed(word)
    return jsonify({
        'matches': matches,
        'run_time': run_time,
    })

print 'Serving HTTP on %s port %s...' % (HOST, PORT)
server = cherrypy.wsgiserver.CherryPyWSGIServer((HOST, PORT), app)
try:
    server.start()
except (KeyboardInterrupt, SystemExit), exc:
    server.stop()
