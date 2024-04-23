from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

routes = Blueprint("routes", __name__, template_folder='../views')

@routes.route('/')
@routes.route('/home')
def hola():
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(404)

@routes.route('/adios')
def adios():
    try:
        return render_template('adios.html')
    except TemplateNotFound:
        abort(404)