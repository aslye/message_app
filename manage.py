from flask.ext.script import Manager, Server
from werkzeug.contrib.fixers import ProxyFix

from app import app

app.wgsi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    threaded=True,
    host='0.0.0.0')
)

if __name__ == "__main__":
    manager.run()
