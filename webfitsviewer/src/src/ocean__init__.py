#from search import app as application
from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, I love Digital Ocean! -src/__init__"
if __name__ == "__main__":
    app.run()
