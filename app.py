from flask import Flask
from blueprints.demo.demo import demo_bp
from blueprints.ifc.ifc import ifc_bp
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.register_blueprint(demo_bp)
app.register_blueprint(ifc_bp)

if __name__ == '__main__':
    app.run(debug=True)