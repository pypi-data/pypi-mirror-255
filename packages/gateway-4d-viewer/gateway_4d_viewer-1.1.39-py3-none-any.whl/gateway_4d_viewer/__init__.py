"""Basic application initialisation."""
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app, resources={r"/*": {"origins": "*"}})

# The import ordering is on purpose to avoid circular imports and simplify the project structure.
# c.f. https://flask.palletsprojects.com/en/latest/patterns/packages/
from gateway_4d_viewer import routes_v1  # noqa: F401, E402
