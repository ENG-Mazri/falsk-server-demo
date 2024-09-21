from flask import Blueprint, render_template

demo_bp = Blueprint("Demo BP", __name__, template_folder="templates")

@demo_bp.route("/demo")
def demo():
    return 'Sup demo blueprint!'

@demo_bp.route("/exportIfc", methods=['POST'])
def exportHandler():
    return render_template('main.html')