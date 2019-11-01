import os
import flask
import Flask
app = Flask(__name__)

@app.route("/")
def hellp_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello {}!\n'.format(target)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
