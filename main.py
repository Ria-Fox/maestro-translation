from translate import api as translate_ns

from flask import Flask
from flask_restx import Api

app = Flask(__name__)
api = Api(title='Maestro translator', description='마에스트로 번역기', version='0.0.1')
api.add_namespace(translate_ns)

api.init_app(app)
app.api = api

if __name__ == '__main__':
    app.run(debug=True)