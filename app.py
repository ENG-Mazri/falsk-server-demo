from flask import Flask

app = Flask(__name__)
                    
@app.route('/')
def hello():
    return 'Sup there!'

@app.route('/test')
def hello2():
    return 'testy testy...'