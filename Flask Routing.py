from flask import *
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/a')
def returnApp():
    return render_template('MainPage.html')

if __name__=='__main__':
    app.run(debug=True)