# source crime/bin/activate 
# flask run --debug

from flask import Flask, request, make_response, render_template
# from config import Config, DevelopmentConfig

from crime import Crime

app = Flask(__name__, template_folder='.')
# app.config.from_object(DevelopmentConfig)

crime = Crime()

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
@app.route('/index', methods=['GET'])
def home():
    return make_response(render_template('index.html',dateBounds=crime.dateBounds()))

@app.route('/options', methods=['GET','POST'])
def options():
    # print(request.form)
    return make_response(render_template('display.html',vis=crime.filterPlot(request.form)))