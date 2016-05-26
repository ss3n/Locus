from flask import Flask, render_template
app = Flask(__name__)

@app.route('/hello')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('publish-ad.html', name=name)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
