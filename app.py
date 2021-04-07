from flask import Flask,render_template

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('hello.html')

if __name__=="__main__":
    app.run(debug=True,use_reloader=False) 